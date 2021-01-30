from django.urls import path

from .views import (
    create_booking,
    generate_payment,
    mark_booking_as_error,
    mark_booking_as_paid,
    register_booking_event,
)

app_name = 'bookings'

urlpatterns = [

    path(r'create/booking/', create_booking,  name='create-booking'),

    path(
        r'payment/success/',
        mark_booking_as_paid,
        name='mark-booking-as-paid'
    ),

    path(
        r'payment/error/',
        mark_booking_as_error,
        name='mark-booking-as-error'
    ),

    path(
        r'register/booking/event/',
        register_booking_event,
        name='register-booking-event'
    ),

    path(
        r'generate/payment/',
        generate_payment,
        name='generate-payment'
    ),

]
