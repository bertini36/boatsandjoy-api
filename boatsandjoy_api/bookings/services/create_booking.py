from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

from django.conf import settings

from boatsandjoy_api.availability.models import Slot
from boatsandjoy_api.bookings.exceptions import NoSlotsSelected
from boatsandjoy_api.bookings.models import Promocode

if TYPE_CHECKING:
    from decimal import Decimal
    from boatsandjoy_api.bookings.payment_gateways import StripePaymentGateway


__all__ = ("CreateBookingRequest", "CreateBookingService",)


@dataclass(frozen=True)
class CreateBookingRequest:
    base_price: Decimal
    slot_ids: list[int]
    customer_name: str
    customer_telephone_number: str
    extras: str
    is_resident: bool
    promocode: str | None = None


class CreateBookingService:
    def __init__(self, payment_gateway: "StripePaymentGateway"):
        self.payment_gateway = payment_gateway

    def execute(self, request: CreateBookingRequest) -> dict:
        booking_day = Slot.objects.get(id=request.slot_ids[0]).day.date
        price = self._apply_discounts(
            booking_day,
            request.base_price,
            request.is_resident,
            request.promocode or None,
        )
        purchase_details = self._build_purchase_details(request.slot_ids, price)
        session_id = self.payment_gateway.checkout(**purchase_details)
        return {
            "price": price,
            "slot_ids": request.slot_ids,
            "customer_name": request.customer_name,
            "customer_telephone_number": request.customer_telephone_number,
            "session_id": session_id,
            "extras": request.extras,
            "promocode": request.promocode,
        }

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
    def _build_purchase_details(slot_ids: list[int], price: "Decimal") -> dict:
        slots = Slot.objects.filter(id__in=slot_ids) \
            .prefetch_related("day", "day__definition__boat") \
            .order_by("position")
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
