# -*- coding: UTF-8 -*-

from django.db import models

from boatsandjoy.core.models import BaseModel
from .constants import BookingStatus


class Booking(BaseModel):
    locator = models.CharField(max_length=20)
    price = models.DecimalField(
        blank=False,
        max_digits=8,
        decimal_places=2,
        help_text='Booking price'
    )
    slots = models.ManyToManyField('availability.Slot')
    customer_name = models.CharField(max_length=100, default='')
    customer_email = models.CharField(max_length=100, default='')
    customer_telephone_number = models.CharField(max_length=100, default='')
    status = models.CharField(
        choices=BookingStatus.STATUS,
        default=BookingStatus.PENDING,
        max_length=10
    )
    session_id = models.CharField(
        max_length=100,
        help_text='Session id',
        blank=True
    )

    def __str__(self) -> str:
        return f'Booking [{self.id}]'

    class Meta:
        verbose_name = 'booking'
        verbose_name_plural = 'bookings'
