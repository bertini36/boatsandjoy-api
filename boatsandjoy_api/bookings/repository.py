import random
import string
from abc import ABC, abstractmethod
from decimal import Decimal
from typing import List

from django.db import DatabaseError

from boatsandjoy_api.availability.models import Slot
from boatsandjoy_api.core.data_adapters import DjangoDataAdapter
from . import domain, models
from .models import BookingStatus
from .exceptions import (
    BookingInvalidDataError,
    BookingNotFound,
    NoSlotsSelected,
)


class BookingsRepository(ABC):
    @classmethod
    @abstractmethod
    def create(
        cls,
        price: Decimal = None,
        slot_ids: List[int] = None,
        customer_name: str = None,
        customer_telephone_number: str = None,
        customer_email: str = None,
        session_id: str = None,
        extras: str = None,
        promocode: str = None,
    ) -> domain.Booking:
        pass

    @classmethod
    @abstractmethod
    def get_purchase_details(cls, price: Decimal, slot_ids: List[int]) -> dict:
        pass

    @classmethod
    @abstractmethod
    def get(
        cls, obj_id: int = None, session_id: str = None, status: str = None
    ) -> domain.Booking:
        pass

    @classmethod
    @abstractmethod
    def mark_as_paid(cls, booking: domain.Booking) -> domain.Booking:
        pass

    @classmethod
    @abstractmethod
    def mark_as_error(cls, booking: domain.Booking) -> domain.Booking:
        pass

    @classmethod
    @abstractmethod
    def update(
        cls,
        booking: domain.Booking,
        customer_email: str = None,
        session_id: str = None,
    ) -> domain.Booking:
        pass


class DjangoBookingsRepository(BookingsRepository):
    DATA_ADAPTER = DjangoDataAdapter

    @classmethod
    def create(
        cls,
        price: Decimal = None,
        slot_ids: List[int] = None,
        customer_name: str = None,
        customer_telephone_number: str = None,
        customer_email: str = None,
        session_id: str = None,
        extras: str = None,
        promocode: str = None,
    ) -> domain.Booking:
        django_data = cls.DATA_ADAPTER.transform(
            price=price,
            customer_name=customer_name,
            customer_telephone_number=customer_telephone_number,
            session_id=session_id,
            customer_email=customer_email,
            locator=cls._generate_locator(),
            extras=extras,
            promocode=promocode,
        )
        try:
            booking = models.Booking.objects.create(**django_data)
            booking.slots.add(*slot_ids)
        except DatabaseError as e:
            raise BookingInvalidDataError(str(e))
        return cls.get_booking_domain_object(booking)

    @classmethod
    def get_purchase_details(cls, price: Decimal, slot_ids: List[int]) -> dict:
        slots = Slot.objects.filter(id__in=slot_ids).order_by("position")
        if not slots:
            raise NoSlotsSelected("A purchase requires slots!")
        first_slot = slots.first()
        last_slot = slots.last()
        boat = first_slot.day.definition.boat
        day = first_slot.day.date
        purchase_details = {
            "name": boat.name,
            "description": (
                f"Renting for {day} from "
                f"{first_slot.from_hour} to {last_slot.to_hour}"
            ),
            "price": price,
        }
        return purchase_details

    @classmethod
    def get(
        cls, obj_id: int = None, session_id: str = None, status: str = None
    ) -> domain.Booking:
        django_filters = cls.DATA_ADAPTER.transform(
            id=obj_id, session_id=session_id, status=status
        )
        try:
            booking = models.Booking.objects.get(**django_filters)
        except models.Booking.DoesNotExist as e:
            raise BookingNotFound(f"Booking not found: {e}")
        return cls.get_booking_domain_object(booking)

    @classmethod
    def mark_as_paid(cls, booking: domain.Booking) -> domain.Booking:
        try:
            booking = models.Booking.objects.get(id=booking.id)
        except models.Booking.DoesNotExist as e:
            raise BookingNotFound(f"Booking not found: {e}")
        booking.status = BookingStatus.CONFIRMED
        booking.save()
        cls._mark_slots_as_booked(booking)
        return cls.get_booking_domain_object(booking)

    @classmethod
    def mark_as_error(cls, booking: domain.Booking) -> domain.Booking:
        try:
            booking = models.Booking.objects.get(id=booking.id)
        except models.Booking.DoesNotExist as e:
            raise BookingNotFound(f"Booking not found: {e}")
        booking.status = BookingStatus.ERROR
        booking.save()
        return cls.get_booking_domain_object(booking)

    @classmethod
    def update(
        cls,
        booking: domain.Booking,
        customer_email: str = None,
        session_id: str = None,
    ) -> domain.Booking:
        try:
            booking = models.Booking.objects.get(id=booking.id)
        except models.Booking.DoesNotExist as e:
            raise BookingNotFound(f"Booking not found: {e}")
        if customer_email:
            booking.customer_email = customer_email
        if session_id:
            booking.session_id = session_id
        booking.save()
        return cls.get_booking_domain_object(booking)

    @classmethod
    def get_booking_domain_object(cls, booking: models.Booking) -> domain.Booking:
        slots = booking.slots.order_by("position")
        boat = slots.first().day.definition.boat
        return domain.Booking(
            id=booking.id,
            locator=booking.locator,
            created=booking.created,
            price=booking.price,
            status=booking.status,
            session_id=booking.session_id,
            boat_id=boat.id,
            boat_name=boat.name,
            slot_ids=list(slots.values_list("id", flat=True)),
            date=slots.first().day.date,
            checkin_hour=slots.first().from_hour,
            checkout_hour=slots.last().to_hour,
            customer_email=booking.customer_email,
            customer_name=booking.customer_name,
            customer_telephone_number=booking.customer_telephone_number,
            extras=booking.extras,
            promocode=booking.promocode,
        )

    @staticmethod
    def _mark_slots_as_booked(booking: models.Booking):
        for slot in booking.slots.all():
            slot.booked = True
            slot.save()

    @staticmethod
    def _generate_locator(length=20):
        return "".join(random.choices(string.ascii_uppercase + string.digits, k=length))
