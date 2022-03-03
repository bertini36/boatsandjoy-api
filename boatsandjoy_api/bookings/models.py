from django.core.validators import validate_slug
from django.db import models

from boatsandjoy_api.core.models import BaseModel
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
        max_length=10,
    )
    session_id = models.CharField(
        max_length=100,
        help_text='Session id', blank=True
    )
    extras = models.TextField(default='')
    promocode = models.CharField(max_length=100, default='')

    def __str__(self) -> str:
        return f'Booking [{self.id}]'

    class Meta:
        verbose_name = 'booking'
        verbose_name_plural = 'bookings'


class Promocode(BaseModel):
    name = models.CharField(max_length=20, validators=[validate_slug])
    valid_from = models.DateField(blank=False)
    valid_to = models.DateField(blank=False)
    factor = models.FloatField(
        blank=False,
        help_text=(
            'You can use it to define discounts with numbers less than '
            '0 Ex: if you need a 20% discount you have to specify 0.8, if you '
            'need to increase price a 50%, you have to specify 1.5 value'
        ),
    )
    limit_of_uses = models.IntegerField(default=10)
    number_of_uses = models.IntegerField(default=0)

    def __str__(self) -> str:
        return f"Promocode [{self.name}]"

    class Meta:
        verbose_name = 'promocode'
        verbose_name_plural = 'promocodes'
