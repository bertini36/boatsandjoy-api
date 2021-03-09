from dataclasses import dataclass
from datetime import date, datetime, time
from decimal import Decimal
from typing import List


@dataclass
class Booking:
    id: int
    locator: str
    created: datetime
    price: Decimal
    status: str
    session_id: str
    boat_id: str
    slot_ids: List[int]
    date: date
    checkin_hour: time
    checkout_hour: time
    customer_name: str
    customer_telephone_number: str
    customer_email: str = None
    extras: str = None
