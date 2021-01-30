# -*- coding: UTF-8 -*-

from dataclasses import dataclass
from datetime import datetime
from typing import List


@dataclass
class Photo:
    url: str
    description: str


@dataclass
class Boat:
    id: int
    created: datetime
    name: str
    description: str
    active: bool
    photos: List[Photo]
