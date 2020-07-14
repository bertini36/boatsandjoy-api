# -*- coding: UTF-8 -*-

from abc import ABC, abstractmethod
from datetime import date, timedelta
from datetime import datetime
from decimal import Decimal
from typing import List

from django.utils.translation import gettext_lazy as _

from boatsandjoy.boats.domain import Boat
from boatsandjoy.core.data_adapters import DjangoDataAdapter
from . import domain
from . import models
from .exceptions import NoDayDefinitionDefined, NoAvailabilityForDay


class AvailabilityRepository(ABC):

    @classmethod
    @abstractmethod
    def filter_days_definitions(
        cls,
        obj_id: int = None,
        boat_id: int = None,
        date_: date = None
    ) -> List[domain.DayDefinition]:
        pass

    @classmethod
    @abstractmethod
    def get_day_definition(
        cls,
        obj_id: int = None,
        boat_id: int = None,
        date_: date = None
    ) -> domain.DayDefinition:
        pass

    @classmethod
    @abstractmethod
    def create_days(
        cls,
        day_definitions: List[domain.DayDefinition],
        from_: date,
        to: date
    ) -> List[domain.Day]:
        pass

    @classmethod
    @abstractmethod
    def create_slots(cls, day: domain.Day) -> List[domain.Slot]:
        pass

    @classmethod
    @abstractmethod
    def filter_price_variations(
        cls,
        obj_id: int = None,
        boat_id: int = None,
        date_: date = None
    ) -> List[domain.PriceVariation]:
        pass

    @classmethod
    @abstractmethod
    def delete_days(cls, days: List[domain.Day]):
        pass

    @classmethod
    @abstractmethod
    def get_day(cls, boat: Boat, date_: date) -> domain.Day:
        pass

    @classmethod
    def get_slot_timing(
        cls,
        day_definition: domain.DayDefinition,
        slot: domain.Slot
    ) -> domain.SlotTiming:
        hours_per_slot = day_definition.hours_per_slot
        delta = timedelta(hours=hours_per_slot * slot.position)
        from_hour = (
            datetime.combine(date(1, 1, 1), day_definition.first_time) + delta
        ).time()
        delta2 = timedelta(hours=day_definition.hours_per_slot)
        to_hour = (
            datetime.combine(date(1, 1, 1), from_hour) + delta2
        ).time()
        return domain.SlotTiming(from_hour=from_hour, to_hour=to_hour)

    @classmethod
    def get_available_slots(cls, day: domain.Day) -> List[domain.Slot]:
        return list(filter(lambda slot: not slot.booked, day.slots))

    @classmethod
    def sort_slots(cls, slots: List[domain.Slot]) -> List[domain.Slot]:
        return sorted(slots, key=lambda slot: slot.position)

    @classmethod
    def get_price_per_hour(cls, boat: Boat, date_: date) -> Decimal:
        day_definition = cls.get_day_definition(boat_id=boat.id, date_=date_)
        price_variations = cls.filter_price_variations(
            boat_id=boat.id,
            date_=date_
        )
        price = day_definition.price_per_hour
        if price_variations:
            price_variation = price_variations[0]
            if price_variation.factor:
                price = (
                    day_definition.price_per_hour * Decimal(price_variation.factor)
                )
        return round(price, 2)


class DjangoAvailabilityRepository(AvailabilityRepository):
    DATA_ADAPTER = DjangoDataAdapter

    @classmethod
    def filter_days_definitions(
        cls,
        obj_id: int = None,
        boat_id: int = None,
        date_: date = None
    ) -> List[domain.DayDefinition]:
        django_filters = cls.DATA_ADAPTER.transform(
            id=obj_id,
            boat_id=boat_id,
            from_date__lte=date_,
            to_date__gte=date_
        )
        day_definitions = models.DayDefinition.objects.filter(**django_filters)
        return [
            cls.get_day_definition_domain_object(day_definition)
            for day_definition in day_definitions
        ]

    @classmethod
    def get_day_definition(
        cls,
        obj_id: int = None,
        boat_id: int = None,
        date_: date = None
    ) -> domain.DayDefinition:
        django_filters = cls.DATA_ADAPTER.transform(
            id=obj_id,
            boat_id=boat_id,
            from_date__lte=date_,
            to_date__gte=date_
        )
        try:
            day_definition = models.DayDefinition.objects.get(**django_filters)
        except models.DayDefinition.DoesNotExist:
            raise NoDayDefinitionDefined(
                _(f'This boat has not a day definition for day {date_}')
            )
        return cls.get_day_definition_domain_object(day_definition)

    @classmethod
    def create_days(
        cls,
        day_definitions: List[domain.DayDefinition],
        from_: date,
        to: date
    ) -> List[domain.Day]:
        days = []
        for i in range(int((to - from_).days)):
            date_ = from_ + timedelta(days=i)
            for day_definition in day_definitions:
                if day_definition.from_date <= date_ <= day_definition.to_date:
                    days.append(
                        models.Day(definition_id=day_definition.id, date=date_)
                    )
                    break
        days = models.Day.objects.bulk_create(days)
        return [cls.get_day_domain_object(day) for day in days]

    @classmethod
    def create_slots(cls, day: domain.Day) -> List[domain.Slot]:
        day_definition = cls.get_day_definition(obj_id=day.day_definition_id)
        slots = []
        for i in range(day_definition.n_slots):
            slot = models.Slot(day_id=day.id, position=i)
            slot_timing = cls.get_slot_timing(day_definition, slot)
            slot.from_hour = slot_timing.from_hour
            slot.to_hour = slot_timing.to_hour
            slots.append(slot)
        slots = models.Slot.objects.bulk_create(slots)
        return [cls.get_slot_domain_object(slot) for slot in slots]

    @classmethod
    def filter_price_variations(
        cls,
        obj_id: int = None,
        boat_id: int = None,
        date_: date = None
    ) -> List[domain.PriceVariation]:
        django_filters = cls.DATA_ADAPTER.transform(
            id=obj_id,
            boat_id=boat_id,
            from_date__lte=date_,
            to_date__gte=date_
        )
        price_variations = models.PriceVariation.objects.filter(
            **django_filters
        )
        return [
            cls.get_price_variation_domain_object(price_variation)
            for price_variation in price_variations
        ]

    @classmethod
    def delete_days(cls, days: List[domain.Day]):
        day_ids = [day.id for day in days]
        models.Day.objects.filter(id__in=day_ids).delete()

    @classmethod
    def get_day(cls, boat: Boat, date_: date) -> domain.Day:
        django_filters = cls.DATA_ADAPTER.transform(
            definition__boat_id=boat.id,
            date=date_
        )
        try:
            day = models.Day.objects.get(**django_filters)
        except models.Day.DoesNotExist:
            raise NoAvailabilityForDay(
                _('There are not day availability definied for this day')
            )
        return cls.get_day_domain_object(day)

    @classmethod
    def get_day_definition_domain_object(
        cls,
        day_definition: models.DayDefinition
    ) -> domain.DayDefinition:
        return domain.DayDefinition(
            id=day_definition.id,
            first_time=day_definition.first_time,
            hours_per_slot=day_definition.hours_per_slot,
            n_slots=day_definition.n_slots,
            price_per_hour=day_definition.price_per_hour,
            from_date=day_definition.from_date,
            to_date=day_definition.to_date,
            description=day_definition.description,
            boat_id=day_definition.boat.id,
            days=[
                cls.get_day_domain_object(day)
                for day in day_definition.days.all()
            ],
            n_slots_deal_threshold=day_definition.n_slots_deal_threshold,
            discount_when_deal=day_definition.discount_when_deal,
            resident_discount=day_definition.resident_discount
        )

    @classmethod
    def get_day_domain_object(cls, day: models.Day) -> domain.Day:
        return domain.Day(
            id=day.id,
            date=day.date,
            day_definition_id=day.definition.id,
            slots=[
                cls.get_slot_domain_object(slot)
                for slot in day.slots.all()
            ]
        )

    @classmethod
    def get_slot_domain_object(cls, slot: models.Slot) -> domain.Slot:
        return domain.Slot(
            id=slot.id,
            position=slot.position,
            from_hour=slot.from_hour,
            to_hour=slot.to_hour,
            booked=slot.booked,
            day_id=slot.day.id
        )

    @classmethod
    def get_price_variation_domain_object(
        cls,
        price_variation: models.PriceVariation
    ) -> domain.PriceVariation:
        return domain.PriceVariation(
            from_date=price_variation.from_date,
            to_date=price_variation.to_date,
            factor=price_variation.factor,
            boat_id=price_variation.boat.id
        )
