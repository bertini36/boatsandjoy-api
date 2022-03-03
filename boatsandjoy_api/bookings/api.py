from dataclasses import asdict
from datetime import date
from decimal import Decimal
from typing import Type

from django.conf import settings
from django.db.models import F

from boatsandjoy_api.availability import models as availability_models
from boatsandjoy_api.boats.api import api as boats_api
from boatsandjoy_api.bookings import models as booking_models
from boatsandjoy_api.bookings.models import Promocode
from boatsandjoy_api.core.responses import (
    ErrorResponseBuilder,
    ResponseBuilder,
    ResponseBuilderInterface,
)
from boatsandjoy_api.core.utils import send_email
from .constants import BookingStatus
from .domain import Booking
from .exceptions import BookingsApiException
from .payment_gateways import PaymentGateway, StripePaymentGateway
from .repository import BookingsRepository, DjangoBookingsRepository
from .requests import (
    CreateBookingRequest, GetBookingBySessionRequest,
    GetBookingRequest, MarkBookingAsErrorRequest,
    RegisterBookingEventRequest,
)
from .validators import (
    BookingCreationRequestValidator,
    GetBookingBySessionRequestValidator,
    GetBookingRequestValidator,
    IdentifyBookingBySessionRequestValidator,
)
from ..boats.requests import FilterBoatsRequest


class BookingsApi:
    def __init__(
        self,
        bookings_repository: Type[BookingsRepository],
        response_builder: Type[ResponseBuilderInterface],
        error_builder: Type[ResponseBuilderInterface],
        payment_gateway: Type[PaymentGateway],
    ):
        self.bookings_repository = bookings_repository
        self.response_builder = response_builder
        self.error_builder = error_builder
        self.payment_gateway = payment_gateway

    def create(self, request: CreateBookingRequest):
        """
        :return {
            'error': bool,
            'data': {
                'id': int,
                'created': datetime,
                'price': Decimal,
                'status': str,
                'session_id': str
            }
        }
        """
        try:
            BookingCreationRequestValidator.validate(request)

            price = request.base_price
            booking_day = availability_models.Slot.objects.get(
                id=request.slot_ids[0]
            ).day.date
            price = self._apply_discounts(
                price,
                request.is_resident,
                request.promocode,
                booking_day,
            )
            purchase_details = self.bookings_repository.get_purchase_details(
                slot_ids=request.slot_ids,
                price=price,
            )
            session_id = self.payment_gateway.generate_checkout_session_id(
                **purchase_details
            )
            booking = self.bookings_repository.create(
                **asdict(request),
                session_id=session_id
            )
            return self.response_builder(booking).build()

        except BookingsApiException as e:
            return self.error_builder(e).build()

    @staticmethod
    def _apply_discounts(
        price: Decimal,
        is_resident: bool,
        promocode: str,
        booking_day: date,
    ) -> Decimal:
        discount = Decimal(0)
        if is_resident:
            discount += Decimal(settings.RESIDENT_DISCOUNT)

        use_day = date.today()
        try:
            promocode = Promocode.objects.get(
                name=promocode,
                use_from__lte=use_day,
                use_to__gte=use_day,
                booking_from__lte=booking_day,
                booking_to__gte=booking_day,
                number_of_uses__lt=F('limit_of_uses'),
            )
            discount += Decimal(promocode.factor)
        except Promocode.DoesNotExist:
            pass

        return price - (price * discount)

    def get(self, request: GetBookingRequest):
        try:
            GetBookingRequestValidator.validate(request)
            request_dict = asdict(request)
            generate_new_session_id = request_dict.pop(
                'generate_new_session_id'
            )
            booking = self.bookings_repository.get(**request_dict)
            if generate_new_session_id:
                purchase_details = (
                    self.bookings_repository.get_purchase_details(
                        slot_ids=booking.slot_ids, price=booking.price
                    )
                )
                session_id = self.payment_gateway.generate_checkout_session_id(
                    **purchase_details
                )
                booking = self.bookings_repository.update(
                    booking=booking,
                    session_id=session_id
                )
            return self.response_builder(booking).build()

        except BookingsApiException as e:
            return self.error_builder(e).build()

    def mark_as_error(self, request: MarkBookingAsErrorRequest):
        try:
            GetBookingBySessionRequestValidator.validate(request)
            booking = self.bookings_repository.get(**asdict(request))
            if booking.status != BookingStatus.CONFIRMED:
                self._send_payment_error_notification_email(booking)
            booking = self.bookings_repository.mark_as_error(booking)
            return self.response_builder(booking).build()

        except BookingsApiException as e:
            return self.error_builder(e).build()

    def register_event(self, request: RegisterBookingEventRequest):
        try:
            event = request.body
            session_id = self.payment_gateway.get_session_id_from_event(event)
            customer_email = self.payment_gateway.get_customer_email_from_event(
                event=event
            )
            booking = self.bookings_repository.get(session_id=session_id)
            booking = self.bookings_repository.update(
                booking=booking,
                customer_email=customer_email
            )
            booking = self.bookings_repository.mark_as_paid(booking)

            promocode = booking_models.Promocode.objects.get(
                code=booking.promocode
            )
            promocode.number_of_uses += 1
            promocode.save()

            self.send_confirmation_email(booking)
            self._send_new_booking_notification_email(booking)
            return self.response_builder([]).build()

        except BookingsApiException as e:
            return self.error_builder(e).build()

    def get_booking_by_session(self, request: GetBookingBySessionRequest):
        try:
            IdentifyBookingBySessionRequestValidator.validate(request)
            request_dict = asdict(request)
            booking = self.bookings_repository.get(**request_dict)
            return self.response_builder(booking).build()

        except BookingsApiException as e:
            return self.error_builder(e).build()

    @staticmethod
    def send_confirmation_email(booking: Booking):
        if booking.customer_email:
            api_request = FilterBoatsRequest(obj_id=booking.boat_id)
            results = boats_api.get(api_request)
            send_email(
                subject='Boats & Joy: Booking confirmation',
                to_email=booking.customer_email,
                template='emails/confirmation.html',
                booking=booking,
                boat=results['data'],
                EMAIL_HOST_USER=settings.EMAIL_HOST_USER,
            )

    @staticmethod
    def _send_new_booking_notification_email(booking: Booking):
        """
        Email sent just for company information
        """
        send_email(
            subject=f'New booking ({booking.locator})',
            to_email=settings.DEFAULT_FROM_EMAIL,
            template='emails/new_booking.html',
            booking=booking,
        )

    @staticmethod
    def _send_payment_error_notification_email(booking: Booking):
        """
        Email sent just for company information
        """
        send_email(
            subject=f'Booking {booking.locator} payment error',
            to_email=settings.DEFAULT_FROM_EMAIL,
            template='emails/payment_error_notification.html',
            booking=booking,
        )


api = BookingsApi(
    DjangoBookingsRepository,
    ResponseBuilder,
    ErrorResponseBuilder,
    StripePaymentGateway,
)
