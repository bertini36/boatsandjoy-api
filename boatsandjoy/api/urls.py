# -*- coding: UTF-8 -*-

from django.urls import path, re_path

from .api_views import (
    get_day_availability,
    get_month_availability,
    create_booking,
    mark_booking_as_paid,
    mark_booking_as_error,
    register_booking_event,
    generate_payment
)
from .template_views import (
    index,
    contact,
    points_of_interest,
    watersports,
    boats,
    cookies
)

app_name = 'api'

urlpatterns = [

    ############################## Templates ###################################

    path('', index, name='index'),

    path('boats/', boats, name='boats'),

    path('contact/', contact, name='contact'),

    path('points-of-interest/', points_of_interest, name='points-of-interest'),

    path('watersports/', watersports, name='watersports'),

    path('cookies/', cookies, name='cookies'),

    ################################# API ######################################

    re_path(
        r'day/(?P<date_>\d{4}-\d{2}-\d{2})/',
        get_day_availability,
        name='get-day-availability'
    ),

    re_path(
        r'month/(?P<date_>\d{4}-\d{2}-\d{2})/',
        get_month_availability,
        name='get-month-availability'
    ),

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
