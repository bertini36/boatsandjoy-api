# -*- coding: UTF-8 -*-

from collections import namedtuple
from dataclasses import dataclass
from datetime import time, date
from decimal import Decimal
from typing import List

from .constants import DayAvailabilityTypes


@dataclass
class Slot:
    id: int
    position: int
    from_hour: time
    to_hour: time
    booked: bool
    day_id: int


@dataclass
class Day:
    id: int
    date: date
    day_definition_id: int
    slots: List[Slot]

    @property
    def availability_type(self):
        n_booked_slots = len(list(filter(lambda slot: slot.booked, self.slots)))
        n_total_slots = len(self.slots)
        if n_booked_slots == n_total_slots:
            return DayAvailabilityTypes.FULL
        elif n_booked_slots > 0:
            return DayAvailabilityTypes.PARTIALLY_FREE
        else:
            return DayAvailabilityTypes.FREE


@dataclass
class DayDefinition:
    id: int
    first_time: time
    hours_per_slot: int
    n_slots: int
    price_per_hour: Decimal
    from_date: date
    to_date: date
    description: str
    boat_id: int
    days: List[Day]
    n_slots_deal_threshold: int
    discount_when_deal: float


@dataclass
class PriceVariation:
    from_date: date
    to_date: date
    factor: float
    boat_id: int


SlotTiming = namedtuple('SlotTiming', ['from_hour', 'to_hour'])
DateRange = namedtuple('DateRange', ['from_date', 'to_date'])
