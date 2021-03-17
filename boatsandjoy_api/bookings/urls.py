from django.urls import path

from .views import (
    create_booking,
    generate_payment,
    mark_booking_as_error,
    register_booking_event,
    get_booking_by_session,
)

app_name = 'bookings'

urlpatterns = [
    path(r'generate/payment/', generate_payment, name='generate-payment'),
    path(r'create/booking/', create_booking, name='create-booking'),
    path(
        r'register/booking/event/',
        register_booking_event,
        name='register-booking-event',
    ),
    path(
        r'mark/booking/as/error/',
        mark_booking_as_error,
        name='mark-booking-as-error'
    ),
    path(
        r'get/booking/by/session/',
        get_booking_by_session,
        name='get-booking-by-session'
    )
]
