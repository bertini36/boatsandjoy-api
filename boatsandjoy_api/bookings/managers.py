from typing import TYPE_CHECKING

from django.db.models import F, QuerySet

if TYPE_CHECKING:
    from datetime import date
    from boatsandjoy_api.bookings.models import Promocode


class PromocodeQuerySet(QuerySet):
    def retrieve(
        self, name: str, use_day: "date", booking_day: "date",
    ) -> "Promocode":
        return self.get(
            name=name,
            use_from__lte=use_day,
            use_to__gte=use_day,
            booking_from__lte=booking_day,
            booking_to__gte=booking_day,
            number_of_uses__lt=F("limit_of_uses"),
        )
