# -*- coding: UTF-8 -*-

from abc import ABC, abstractmethod
from datetime import date
from typing import List

from django.utils.translation import gettext_lazy as _

from boatsandjoy_api.boats.domain import Boat
from .exceptions import NoDayDefinitionDefined, AvailabilityAlreadyCreated
from .repository import DjangoAvailabilityRepository


class AvailabilityGeneratorInterface(ABC):

    @abstractmethod
    def generate(self, year: int = date.today().year) -> List[dict]:
        pass

    @abstractmethod
    def delete(self, year: int = date.today().year):
        pass


class AvailabilityGenerator(AvailabilityGeneratorInterface):

    def __init__(self, boat: Boat):
        self.boat = boat
        self.day_definitions = (
            DjangoAvailabilityRepository.filter_days_definitions(
                boat_id=self.boat.id
            )
        )
        if not self.day_definitions:
            raise NoDayDefinitionDefined(
                _('This boat has not day definitions defined')
            )

    def generate(self, year: int = date.today().year) -> List[dict]:
        if self._exists_availability_for(year):
            raise AvailabilityAlreadyCreated(
                _(f'Availabilty already exists for year {year}')
            )
        start_date = date(year, 1, 1)
        end_date = date(year, 12, 31)
        days = DjangoAvailabilityRepository.create_days(
            day_definitions=self.day_definitions,
            from_=start_date,
            to=end_date
        )
        return [
            {
                'day': day,
                'slots': DjangoAvailabilityRepository.create_slots(day=day)
            } for day in days
        ]

    def delete(self, year: int = date.today().year):
        for day_definition in self.day_definitions:
            days = list(
                filter(lambda day: day.date.year == year, day_definition.days)
            )
            DjangoAvailabilityRepository.delete_days(days)

    def _exists_availability_for(self, year: int = date.today().year) -> bool:
        for day_definition in self.day_definitions:
            if any([day.date.year == year for day in day_definition.days]):
                return True
        return False
