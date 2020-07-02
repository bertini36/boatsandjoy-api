# -*- coding: UTF-8 -*-

from dataclasses import dataclass
from decimal import Decimal
from typing import List


@dataclass
class CreateBookingRequest:
    price: Decimal
    slot_ids: List[int]
    customer_name: str
    customer_telephone_number: str


@dataclass
class GetBookingRequest:
    obj_id: int
    generate_new_session_id: bool


@dataclass
class MarkBookingAsPaidRequest:
    session_id: str


@dataclass
class MarkBookingAsErrorRequest:
    session_id: str


@dataclass
class RegisterBookingEventRequest:
    headers: dict
    body: dict