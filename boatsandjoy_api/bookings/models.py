from enum import Enum

from django.conf import settings
from django.core.validators import validate_slug
from django.db import models

from boatsandjoy_api.bookings.managers import PromocodeQuerySet
from boatsandjoy_api.core.models import BaseModel
from boatsandjoy_api.core.utils import send_email


class BookingStatus(Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    ERROR = "error"

    @classmethod
    def to_django_choices(cls) -> tuple:
        return (
            (cls.PENDING, "Pending"),
            (cls.CONFIRMED, "Confirmed"),
            (cls.ERROR, "Error"),
        )


class Booking(BaseModel):
    locator = models.CharField(max_length=20)
    price = models.DecimalField(
        blank=False, max_digits=8, decimal_places=2, help_text="Booking price"
    )
    slots = models.ManyToManyField("availability.Slot")
    customer_name = models.CharField(max_length=100, default="")
    customer_email = models.CharField(max_length=100, default="")
    customer_telephone_number = models.CharField(max_length=100, default="")
    status = models.CharField(
        choices=BookingStatus.to_django_choices(),
        default=BookingStatus.PENDING,
        max_length=10,
    )
    session_id = models.CharField(max_length=100, help_text="Session id", blank=True)
    extras = models.TextField(default="")
    promocode = models.CharField(max_length=100, default="")

    def __str__(self) -> str:
        return f"Booking [{self.id}]"

    class Meta:
        verbose_name = "booking"
        verbose_name_plural = "bookings"

    def pay(self, customer_email: str):
        self.customer_email = customer_email
        self.status = BookingStatus.CONFIRMED
        self.save()
        self.slots.update(booked=True)

    def send_confirmation_email(self):
        if self.customer_email:
            boat = self.slots.first().day.definition.boat
            send_email(
                subject="Boats & Joy: Booking confirmation",
                to_email=self.customer_email,
                template="emails/confirmation.html",
                booking=self,
                boat=boat,
                EMAIL_HOST_USER=settings.EMAIL_HOST_USER,
            )

    def send_new_booking_notification_email(self):
        send_email(
            subject=f"New booking ({self.locator})",
            to_email=settings.DEFAULT_FROM_EMAIL,
            template="emails/new_booking.html",
            booking=self,
        )


class Promocode(BaseModel):
    name = models.CharField(max_length=20, validators=[validate_slug])
    use_from = models.DateField(blank=False)
    use_to = models.DateField(blank=False)
    booking_from = models.DateField(blank=False)
    booking_to = models.DateField(blank=False)
    factor = models.FloatField(
        blank=False,
        help_text=(
            "You can use it to define discounts with numbers less than "
            "0 Ex: if you need a 20% discount you have to specify 0.8, if you "
            "need to increase price a 50%, you have to specify 1.5 value"
        ),
    )
    limit_of_uses = models.IntegerField(default=10)
    number_of_uses = models.IntegerField(default=0)

    objects = PromocodeQuerySet.as_manager()

    def __str__(self) -> str:
        return f"Promocode [{self.name}]"

    class Meta:
        verbose_name = "promocode"
        verbose_name_plural = "promocodes"

    def increase_uses(self):
        self.number_of_uses += 1
        self.save()
