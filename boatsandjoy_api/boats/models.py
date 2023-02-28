from django.db import models

from boatsandjoy_api.boats.managers import BoatQuerySet
from boatsandjoy_api.core.models import BaseModel


class Boat(BaseModel):
    name = models.CharField(max_length=200)
    active = models.BooleanField(default=True)

    objects = BoatQuerySet.as_manager()

    def __str__(self) -> str:
        return f"{self.name}"

    class Meta:
        verbose_name = "boat"
        verbose_name_plural = "boats"
