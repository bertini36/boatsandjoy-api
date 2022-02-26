from dataclasses import dataclass
from decimal import Decimal
from typing import List, Optional


@dataclass
class CreateBookingRequest:
    price: Decimal
    slot_ids: List[int]
    customer_name: str
    customer_telephone_number: str
    extras: str
    is_resident: bool
    promocode: Optional[str] = None


@dataclass
class GetBookingRequest:
    obj_id: int
    generate_new_session_id: bool


@dataclass
class MarkBookingAsErrorRequest:
    session_id: str


@dataclass
class RegisterBookingEventRequest:
    headers: dict
    body: dict


@dataclass
class GetBookingBySessionRequest:
    session_id: str
