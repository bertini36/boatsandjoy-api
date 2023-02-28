from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

from django.conf import settings

from boatsandjoy_api.availability.models import Slot
from boatsandjoy_api.bookings.models import Booking, Promocode

if TYPE_CHECKING:
    from decimal import Decimal
    from boatsandjoy_api.bookings.payment_gateways import StripePaymentGateway

__all__ = ("CreateBookingRequest", "BookingsService",)


@dataclass(frozen=True)
class CreateBookingRequest:
    base_price: Decimal
    slot_ids: list[str]
    customer_name: str
    customer_telephone_number: str
    extras: str
    is_resident: bool
    promocode: str | None = None


class BookingsService:
    def __init__(self, payment_gateway: "StripePaymentGateway"):
        self.payment_gateway = payment_gateway

    def create(self, request: CreateBookingRequest) -> Booking:
        booking_day = Slot.objects.filter(id=request.slot_ids[0])\
                                  .prefetch_related("day")\
                                  .get().day.date
        price = self._apply_discounts(
            booking_day,
            request.base_price,
            request.is_resident,
            request.promocode,
        )
        purchase_details = self._get_purchase_details(request.slot_ids, price)
        session_id = self.payment_gateway.checkout(**purchase_details)
        return Booking.objects.create(
            price=price,
            slot_ids=request.slot_ids,
            customer_name=request.customer_name,
            customer_telephone_number=request.customer_telephone_number,
            session_id=session_id,
            extras=request.extras,
            promocode=request.promocode,
        )

    def force_checkout(self, booking: "Booking") -> "Booking":
        purchase_details = self._get_purchase_details(
            slot_ids=list(booking.slots.values_list("id", flat=True)),
            price=booking.price,
        )
        session_id = self.payment_gateway.checkout(**purchase_details)
        Booking.objects.update(id=booking.id, session_id=session_id)
        booking.refresh_from_db()
        return booking

    def register_payment(self, event: dict):
        session_id = self.payment_gateway.get_session_id_from_event(event)
        booking = Booking.objects.get(session_id=session_id)
        customer_email = self.payment_gateway.get_customer_email_from_event(event)
        booking.pay(customer_email)

        if booking.promocode:
            booking.promocode.increase_uses()

        booking.send_confirmation_email()
        booking.send_new_booking_notification_email()

    @staticmethod
    def _apply_discounts(
        booking_day: date,
        price: Decimal,
        is_resident: bool,
        promocode_name: str | None = None,
    ) -> Decimal:
        discount = Decimal(0)
        if is_resident:
            discount += Decimal(settings.RESIDENT_DISCOUNT)

        if promocode_name:
            use_day = date.today()
            promocode = Promocode.objects.retrieve(
                promocode_name, use_day, booking_day,
            )
            discount += Decimal(promocode.factor)

        return price - (price * discount)

    @staticmethod
    def _get_purchase_details(slot_ids: list[str], price: "Decimal") -> dict:
        slots = Slot.objects.filter(id__in=slot_ids) \
                            .prefetch_related("day", "day__definition__boat") \
                            .order_by("position")
        first_slot = slots.first()
        last_slot = slots.last()
        boat = first_slot.day.definition.boat
        day = first_slot.day.date
        purchase_details = {
            "name": boat.name,
            "description": f"Renting for {day} from {first_slot.from_hour} to {last_slot.to_hour}",
            "price": price,
        }
        return purchase_details
