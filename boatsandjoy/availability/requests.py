# -*- coding: UTF-8 -*-

from dataclasses import dataclass
from datetime import date


@dataclass
class GetDayAvailabilityRequest:
    date: date


@dataclass
class GetMonthAvailabilityRequest:
    month: int
    year: int
