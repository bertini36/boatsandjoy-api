from django.contrib import admin, messages
from django.db.models import QuerySet
from django.http import HttpRequest
from django.utils.safestring import mark_safe

from boatsandjoy_api.core.exceptions import BoatsAndJoyException
from .constants import BookingStatus
from .exceptions import BookingAlreadyConfirmed, BookingAlreadyPending
from .models import Booking


def confirm_booking(modeladmin, request: HttpRequest, queryset: QuerySet):
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


def unconfirm_booking(modeladmin, request: HttpRequest, queryset: QuerySet):
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
        'created',
        'locator',
        'status',
        'get_date_and_hours',
        'get_price',
        'session_id',
        'customer_name',
        'customer_email',
        'get_payment_url',
    )
    actions = [confirm_booking, unconfirm_booking]

    def get_date_and_hours(self, obj: Booking) -> str:
        slots = obj.slots.all()
        first_slot = slots.first()
        last_slot = slots.last()
        time_str = ''
        if first_slot and last_slot:
            day = first_slot.day.date if first_slot.day else ''
            time_str = (
                f'{day}: from {first_slot.from_hour} to ' f'{last_slot.to_hour}'
            )
        return time_str

    get_date_and_hours.short_description = 'Date and hours'

    @staticmethod
    def get_price(obj: Booking) -> str:
        return f'{obj.price}€'

    def get_payment_url(self, obj: Booking) -> str:
        if obj.status == BookingStatus.PENDING:
            url = f'/generate/payment/?booking_id={obj.id}'
            return mark_safe(
                f'<a href="{url}" target="_blank" class="button">Pay</a>'
            )
        return ''

    get_payment_url.short_description = 'Payment url'


admin.site.register(Booking, BookingAdmin)
