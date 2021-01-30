from dataclasses import dataclass


@dataclass
class FilterBoatsRequest:
    obj_id: str = None
    name: str = None
    active: bool = None
