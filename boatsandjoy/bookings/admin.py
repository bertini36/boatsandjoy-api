# -*- coding: UTF-8 -*-

from django.contrib import admin
from django.contrib import messages
from django.db.models import QuerySet
from django.http import HttpRequest
from django.utils.safestring import mark_safe

from boatsandjoy.core.exceptions import BoatsAndJoyException
from boatsandjoy.core.utils import format_date
from .constants import BookingStatus
from .exceptions import BookingAlreadyPending, BookingAlreadyConfirmed
from .models import Booking


def confirm_booking(
    modeladmin,
    request: HttpRequest,
    queryset: QuerySet
):
    for booking in queryset:
        try:
            if booking.status == BookingStatus.CONFIRMED:
                raise BookingAlreadyConfirmed(
                    f'Booking {booking.locator} already confirmed!'
                )
            booking.status = BookingStatus.CONFIRMED
            booking.save()
            for slot in booking.slots.all():
                slot.booked = True
                slot.save()

        except BoatsAndJoyException as e:
            messages.add_message(request, messages.ERROR, str(e))


def unconfirm_booking(
    modeladmin,
    request: HttpRequest,
    queryset: QuerySet
):
    for booking in queryset:
        try:
            if booking.status == BookingStatus.PENDING:
                raise BookingAlreadyPending(
                    f'Booking {booking.locator} already pending!'
                )
            booking.status = BookingStatus.PENDING
            booking.save()
            for slot in booking.slots.all():
                slot.booked = False
                slot.save()

        except BoatsAndJoyException as e:
            messages.add_message(request, messages.ERROR, str(e))


class BookingAdmin(admin.ModelAdmin):
    list_filter = ('status',)
    search_fields = ('locator', 'session_id', 'customer_email')
    list_display = (
        'created', 'locator', 'status', 'get_date_and_hours', 'get_price',
        'session_id', 'customer_name', 'customer_email', 'get_payment_url'
    )
    actions = [
        confirm_booking,
        unconfirm_booking
    ]

    @staticmethod
    def get_date_and_hours(obj: Booking) -> str:
        slots = obj.slots.all()
        first_slot = slots.first()
        last_slot = slots.last()
        day = format_date(first_slot.day.date) if first_slot.day else ''
        return f'{day}: from {first_slot.from_hour} to {last_slot.to_hour}'

    @staticmethod
    def get_price(obj: Booking) -> str:
        return f'{obj.price}€'

    @staticmethod
    def get_payment_url(obj: Booking) -> str:
        if obj.status == BookingStatus.PENDING:
            url = f'/generate/payment/?booking_id={obj.id}'
            return mark_safe(
                f'<a href="{url}" target="_blank" class="button">Pay</a>'
            )
        return ''


admin.site.register(Booking, BookingAdmin)
