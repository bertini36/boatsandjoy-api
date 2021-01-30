from dataclasses import dataclass
from datetime import datetime


@dataclass
class Boat:
    id: int
    created: datetime
    name: str
    active: bool
