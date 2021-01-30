from copy import deepcopy
from datetime import date
from decimal import Decimal
from typing import List, Type

from boatsandjoy_api.availability.exceptions import (
    NoAvailabilityForDay,
    NoDayDefinitionDefined,
)
from boatsandjoy_api.boats.api import api as boats_api
from boatsandjoy_api.boats.domain import Boat
from boatsandjoy_api.boats.exceptions import NoActiveBoat
from boatsandjoy_api.boats.requests import FilterBoatsRequest
from boatsandjoy_api.core.exceptions import BoatsAndJoyException
from boatsandjoy_api.core.responses import (
    ResponseBuilder,
    ResponseBuilderInterface,
)
from . import domain
from .constants import DayAvailabilityTypes
from .exceptions import (
    AvailabilityApiException, CombinationOfSize0,
    NoSameDaySlots, NoSlotsAvailable,
)
from .repository import AvailabilityRepository, DjangoAvailabilityRepository
from .requests import GetDayAvailabilityRequest, GetMonthAvailabilityRequest
from .utils import month_date_iter
from .validators import (
    GetAvailabilityRequestValidator,
    GetMonthAvailabilityRequestValidator,
)


class AvailabilityApi:

    def __init__(
        self,
        availability_repository: Type[AvailabilityRepository],
        response_builder: Type[ResponseBuilderInterface]
    ):
        self.availability_repository = availability_repository
        self.response_builder = response_builder

    def get_day_availability(self, request: GetDayAvailabilityRequest) -> dict:
        """
        :return: {
            'error': bool,
            'data': [
                {
                    'boat': boat,
                    'availability': [
                        {
                            'slots': combination,
                            'price': float,
                            'from_hour': time,
                            'to_hour': time
                        },
                        ...
                },
                ...
            ]
        }
        """
        try:
            GetAvailabilityRequestValidator.validate(request)
            results = boats_api.filter(FilterBoatsRequest(active=True))
            boats = [Boat(**boat_data) for boat_data in results['data']]
            availablity_results = self._get_day_availability(
                boats=boats,
                date_=request.date,
                apply_resident_discount=request.apply_resident_discount
            )
            return self.response_builder(availablity_results).build()

        except AvailabilityApiException:
            return self.response_builder([]).build()

    def get_month_availability(
        self,
        request: GetMonthAvailabilityRequest
    ) -> dict:
        """
        :return: {
            'error': bool,
            'data': [
                {
                    'name': 'DayAvailabilityTypes',
                    'date': 'YYYY-MM-DD',
                    'disabled': bool
                },
                ...
            ]
        }
        """
        try:
            GetMonthAvailabilityRequestValidator.validate(request)
            results = boats_api.filter(FilterBoatsRequest(active=True))
            boats = [Boat(**boat_data) for boat_data in results['data']]
            month_availability_results = self._get_month_availability(
                boats=boats,
                month=request.month,
                year=request.year
            )
            return self.response_builder(month_availability_results).build()

        except AvailabilityApiException:
            return self.response_builder(
                self._generate_no_availability_month(request)
            ).build()

    def _get_day_availability(
        self,
        boats: List[Boat],
        date_: date,
        apply_resident_discount: bool
    ) -> list:
        results = []
        for boat in boats:
            try:
                if not boat.active:
                    raise NoActiveBoat('This boat is not active')
                results.append(
                    self._get_boat_response(
                        boat,
                        date_,
                        apply_resident_discount
                    )
                )
            except BoatsAndJoyException:
                continue
        return results

    def _get_month_availability(
        self,
        boats: List[Boat],
        month: int,
        year: int
    ) -> list:
        results = []
        disabled_states = (
            DayAvailabilityTypes.NO_AVAIL,
            DayAvailabilityTypes.FULL
        )
        for idate in month_date_iter(year, month):
            global_day_availability_type = (
                self._get_global_day_availability_type(boats, idate)
            )
            result = {
                'name': global_day_availability_type,
                'date': idate,
                'disabled': global_day_availability_type in disabled_states
            }
            results.append(result)
        return results

    def _get_boat_response(
        self,
        boat: Boat,
        date_: date,
        apply_resident_discount: bool
    ) -> dict:
        day_definition = DjangoAvailabilityRepository.get_day_definition(
            boat_id=boat.id,
            date_=date_
        )
        day = DjangoAvailabilityRepository.get_day(boat, date_)
        available_slots = DjangoAvailabilityRepository.get_available_slots(day)
        combinations = self._get_combinations(available_slots)
        combinations_prices = self._get_combinations_prices(
            boat,
            day,
            combinations
        )
        combinations_timings = self._get_combinations_timing(
            day_definition=day_definition,
            combinations=combinations
        )
        return {
            'boat': {
                'id': boat.id,
                'name': boat.name,
                'description': boat.description,
                'photos': [
                    {'url': photo.url, 'description': photo.description}
                    for photo in boat.photos
                ]
            },
            'availability': [
                {
                    'slots': [
                        {
                            'id': slot.id,
                            'position': slot.position,
                            'from_hour': slot.from_hour,
                            'to_hour': slot.to_hour
                        }
                        for slot in combination
                    ],
                    'price': self._apply_discounts(
                        combination,
                        combinations_prices[i],
                        day_definition,
                        apply_resident_discount
                    ),
                    'from_hour': combinations_timings[i].from_hour,
                    'to_hour': combinations_timings[i].to_hour
                }
                for i, combination in enumerate(combinations)
            ]
        }

    def _get_combinations(
        self,
        slots: List[domain.Slot]
    ) -> List[List[domain.Slot]]:
        """
        Two slots can be at the same combination just
        if they have correlated positions into the same day
        """
        self._check_slots(slots)
        slots = DjangoAvailabilityRepository.sort_slots(slots=slots)
        combinations = []
        for slot1 in slots:
            combination = [slot1]
            combinations = self._add_combination(combinations, combination)
            aux_slot = deepcopy(slot1)
            for slot2 in slots:
                if aux_slot.position == slot2.position:
                    continue
                if aux_slot.position > slot2.position:
                    continue
                if abs(aux_slot.position - slot2.position) != 1:
                    break
                combination.append(slot2)
                combinations = self._add_combination(combinations, combination)
                aux_slot = deepcopy(slot2)
        return combinations

    @staticmethod
    def _check_slots(slots: List[domain.Slot]):
        if not slots:
            raise NoSlotsAvailable('No slots available for this day')
        slot0_day_id = slots[0].day_id
        if any(slot.day_id != slot0_day_id for slot in slots):
            raise NoSameDaySlots('Error: Slots don\'t belong to same day')

    @staticmethod
    def _add_combination(
        combinations: List[List[domain.Slot]],
        combination: List[domain.Slot]
    ) -> List[List[domain.Slot]]:
        combinations.append(deepcopy(combination))
        return combinations

    @staticmethod
    def _get_combinations_prices(
        boat: Boat,
        day: domain.Day,
        combinations: List[List[domain.Slot]]
    ) -> List[Decimal]:
        day_definition = DjangoAvailabilityRepository.get_day_definition(
            boat_id=boat.id,
            date_=day.date
        )
        hours_per_slot = day_definition.hours_per_slot
        day_price_per_hour = DjangoAvailabilityRepository.get_price_per_hour(
            boat=boat,
            date_=day.date
        )
        return [
            len(combination) * hours_per_slot * day_price_per_hour
            for combination in combinations
        ]

    @staticmethod
    def _get_combinations_timing(
        day_definition: domain.DayDefinition,
        combinations: List[List[domain.Slot]]
    ) -> List[domain.SlotTiming]:
        slot_combination_hour_limits = []
        for combination in combinations:
            if len(combination) == 0:
                raise CombinationOfSize0('Error: Combination of size 0')
            elif len(combination) == 1:
                slot_combination_hour_limits.append(
                    DjangoAvailabilityRepository.get_slot_timing(
                        day_definition=day_definition,
                        slot=combination[0]
                    )
                )
            elif len(combination) > 1:
                from_hour = DjangoAvailabilityRepository.get_slot_timing(
                    day_definition=day_definition,
                    slot=combination[0]
                ).from_hour
                to_hour = DjangoAvailabilityRepository.get_slot_timing(
                    day_definition=day_definition,
                    slot=combination[-1]
                ).to_hour
                slot_combination_hour_limits.append(
                    domain.SlotTiming(from_hour=from_hour, to_hour=to_hour)
                )
        return slot_combination_hour_limits

    @staticmethod
    def _get_global_day_availability_type(
        boats: List[Boat],
        date_: date
    ) -> str:
        boats_day_availability_types = []
        if date_ < date.today():
            return DayAvailabilityTypes.NO_AVAIL
        for boat in boats:
            try:
                boats_day_availability_types.append(
                    DjangoAvailabilityRepository.get_day(
                        boat=boat,
                        date_=date_
                    ).availability_type
                )
            except (NoDayDefinitionDefined, NoAvailabilityForDay):
                boats_day_availability_types.append(
                    DayAvailabilityTypes.NO_AVAIL
                )
        if all(
            elem == boats_day_availability_types[0]
            for elem in boats_day_availability_types
        ):
            if boats_day_availability_types:
                global_day_availability_type = boats_day_availability_types[0]
            else:
                global_day_availability_type = DayAvailabilityTypes.NO_AVAIL
        elif (
            DayAvailabilityTypes.PARTIALLY_FREE in boats_day_availability_types
            or DayAvailabilityTypes.FREE in boats_day_availability_types
        ):
            global_day_availability_type = DayAvailabilityTypes.PARTIALLY_FREE
        else:
            global_day_availability_type = DayAvailabilityTypes.FULL
        return global_day_availability_type

    @staticmethod
    def _generate_no_availability_month(request: GetMonthAvailabilityRequest):
        results = []
        for idate in month_date_iter(request.year, request.month):
            results.append({
                'name': DayAvailabilityTypes.NO_AVAIL,
                'date': idate,
                'disabled': True
            })
        return results

    @staticmethod
    def _apply_discounts(
        combination: List[domain.Slot],
        theoretical_price: Decimal,
        day_definition: domain.DayDefinition,
        apply_resident_discount: bool
    ) -> Decimal:
        price = theoretical_price
        if (
            len(combination) >= day_definition.n_slots_deal_threshold and
            day_definition.discount_when_deal
        ):
            price = (
                theoretical_price -
                theoretical_price * Decimal(day_definition.discount_when_deal)
            )
        if apply_resident_discount:
            price = price - price * Decimal(day_definition.resident_discount)
        return round(price, 2)


api = AvailabilityApi(
    DjangoAvailabilityRepository,
    ResponseBuilder
)
