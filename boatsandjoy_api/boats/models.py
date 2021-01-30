from django.db import models

from boatsandjoy_api.core.models import BaseModel
from .constants import BoatConstants


class Boat(BaseModel):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    active = models.BooleanField(default=True)

    def __str__(self) -> str:
        return f'{self.name}'

    class Meta:
        verbose_name = 'boat'
        verbose_name_plural = 'boats'


class Photo(BaseModel):
    boat = models.ForeignKey(
        Boat,
        related_name='photos',
        on_delete=models.CASCADE
    )
    image = models.ImageField(upload_to=BoatConstants.BOATS_PHOTOS_PATH)
    description = models.TextField(blank=True)

    def __str__(self) -> str:
        return f'{self.image} photo'

    class Meta:
        verbose_name = 'photo'
        verbose_name_plural = 'photos'

