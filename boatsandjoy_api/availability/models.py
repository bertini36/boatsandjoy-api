from datetime import time

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from boatsandjoy_api.boats.models import Boat
from boatsandjoy_api.core.models import BaseModel


class DayDefinition(BaseModel):
    """
    This model has to be used to define the type of
    day to reflect the availability of a boat in a single day
    """
    boat = models.ForeignKey(
        Boat,
        related_name='day_definitions',
        on_delete=models.CASCADE
    )
    first_time = models.TimeField(
        default=time(hour=9),
        help_text='Time when the day starts'
    )
    hours_per_slot = models.IntegerField(
        default=2,
        validators=[MaxValueValidator(24), MinValueValidator(1)],
        help_text='How many hours define a slot'
    )
    n_slots = models.IntegerField(
        default=0,
        help_text='Number of availability slots in a single day'
    )
    price_per_hour = models.DecimalField(
        null=False,
        max_digits=8,
        decimal_places=2,
        help_text='Price per hour in euros',
        default=0.0
    )
    from_date = models.DateField(
        blank=False,
        help_text='Since which date this definition is available'
    )
    to_date = models.DateField(
        blank=False,
        help_text='Until which date this definition is available'
    )
    description = models.TextField(blank=True)
    n_slots_deal_threshold = models.IntegerField(
        default=0,
        help_text=(
            'Number of slots that has to have an availability result to be '
            'considered as a good deal'
        )
    )
    discount_when_deal = models.FloatField(
        default=0.0,
        help_text=(
            'Discount applied when availability result is composed by more than'
            ' n_slots_deal_threshold slots'
        )
    )
    resident_discount = models.FloatField(
        default=0.25,
        help_text=(
            'Discount applicable to Balearic islands residents'
        )
    )

    def __str__(self) -> str:
        return f'<Day definition that starts at {self.first_time}, ' \
               f'with {self.n_slots} slots of {self.hours_per_slot} ' \
               f'hours each and with a price of {self.price_per_hour}€ per ' \
               f'hour from {self.from_date} ' \
               f'to {self.to_date}>'

    class Meta:
        verbose_name = 'day definition'
        verbose_name_plural = 'day definition'


class Day(BaseModel):
    definition = models.ForeignKey(
        DayDefinition,
        related_name='days',
        on_delete=models.CASCADE
    )
    date = models.DateField()

    def __str__(self) -> str:
        return str(self.date)

    @property
    def boat(self):
        return self.definition.boat

    class Meta:
        verbose_name = 'day'
        verbose_name_plural = 'days'
        ordering = ('date',)


class Slot(BaseModel):
    """
    An instance of this model represents the minimum bookable time of a boat
    (DayDefinition avoids to define how many slots are in a single day)
    """
    day = models.ForeignKey(Day, related_name='slots', on_delete=models.CASCADE)
    position = models.IntegerField(help_text='Slot position into day')
    from_hour = models.TimeField(help_text='Time at which the slot starts')
    to_hour = models.TimeField(help_text='Time at which the slot ends')
    booked = models.BooleanField(default=False)

    def __str__(self) -> str:
        slot_str = f'Slot {self.day} from {self.from_hour} to {self.to_hour} ' \
                   f'of {self.day.definition.boat}'
        if self.booked:
            return f'{slot_str} booked'
        return f'{slot_str} available'

    class Meta:
        verbose_name = 'slot'
        verbose_name_plural = 'slots'
        ordering = ('position',)


class PriceVariation(BaseModel):
    boat = models.ForeignKey(
        Boat,
        related_name='price_variations',
        on_delete=models.CASCADE
    )
    from_date = models.DateField(blank=False)
    to_date = models.DateField(blank=False)
    factor = models.FloatField(
        blank=False,
        help_text=(
            'You can use it to define discounts with numbers less than '
            '0 and to define increments with numbers greater than 0. Ex: '
            'if you need a 20% discount you have to specify 0.8, if you '
            'need to increase price a 50%, you have to specify 1.5 value'
        )
    )

    def __str__(self) -> str:
        return f'Variation of {self.factor} factor from ' \
               f'{self.from_date} to {self.to_date}'

    class Meta:
        verbose_name = 'price variation'
        verbose_name_plural = 'price variations'


