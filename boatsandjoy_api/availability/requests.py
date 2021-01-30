from dataclasses import dataclass
from datetime import date


@dataclass
class GetDayAvailabilityRequest:
    date: date
    apply_resident_discount: bool


@dataclass
class GetMonthAvailabilityRequest:
    month: int
    year: int
