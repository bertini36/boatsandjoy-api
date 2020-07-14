# -*- coding: UTF-8 -*-

import json

from django.http import HttpRequest, JsonResponse, HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from boatsandjoy.availability.api import api as availability_api
from boatsandjoy.availability.requests import (
    GetDayAvailabilityRequest,
    GetMonthAvailabilityRequest
)
from boatsandjoy.bookings.api import api as bookings_api
from boatsandjoy.bookings.requests import (
    CreateBookingRequest,
    MarkBookingAsPaidRequest,
    MarkBookingAsErrorRequest,
    RegisterBookingEventRequest,
    GetBookingRequest
)
from boatsandjoy.core.utils import transform_to_internal_date


@require_http_methods(['GET'])
def get_day_availability(request: HttpRequest, date_: str) -> JsonResponse:
    """
    :return: {
        'error': bool,
        'data': [
            {
                'boat': boat,
                'availability': [
                    {
                        'slots': combination,
                        'price': float,
                        'from_hour': time,
                        'to_hour': time
                    },
                    ...
            },
            ...
        ]
    }
    """
    date_ = transform_to_internal_date(date_)
    apply_resident_discount = bool(int(request.GET['apply_resident_discount']))
    api_request = GetDayAvailabilityRequest(
        date=date_,
        apply_resident_discount=apply_resident_discount
    )
    results = availability_api.get_day_availability(api_request)
    return JsonResponse(results)


@require_http_methods(['GET'])
def get_month_availability(request: HttpRequest, date_: str) -> JsonResponse:
    """
    :return: {
        'error': bool,
        'data': [
            {
                'name': 'DayAvailabilityTypes',
                'date': 'YYYY-MM-DD',
                'disabled': bool
            },
            ...
        ]
    }
    """
    date_ = transform_to_internal_date(date_)
    api_request = GetMonthAvailabilityRequest(
        month=date_.month,
        year=date_.year
    )
    results = availability_api.get_month_availability(request=api_request)
    return JsonResponse(results)


@csrf_exempt
@require_http_methods(['POST'])
def create_booking(request: HttpRequest) -> JsonResponse:
    """
    :return {
        'error': bool,
        'data': {
            'id': int,
            'created': datetime,
            'price': Decimal,
            'status': str,
            'session_id': str
        }
    }
    """
    data = json.loads(request.body)
    api_request = CreateBookingRequest(
        price=data['price'],
        slot_ids=[int(slot_id) for slot_id in data['slot_ids'].split(',')],
        customer_name=data['customer_name'],
        customer_telephone_number=data['customer_telephone_number']
    )
    results = bookings_api.create(api_request)
    return JsonResponse(results)


@require_http_methods(['GET'])
def mark_booking_as_paid(request):
    session_id = request.GET['session_id']
    api_request = MarkBookingAsPaidRequest(session_id=session_id)
    results = bookings_api.mark_as_paid(api_request)
    return render(
        request,
        'pages/payment_success.html',
        context=results['data']
    )


@require_http_methods(['GET'])
def mark_booking_as_error(request):
    session_id = request.GET.get('session_id')
    data = None
    if session_id:
        api_request = MarkBookingAsErrorRequest(session_id=session_id)
        results = bookings_api.mark_as_error(api_request)
        data = {'booking': results['data']}
    return render(
        request,
        'pages/payment_error.html',
        context=data
    )


@csrf_exempt
def register_booking_event(request):
    api_request = RegisterBookingEventRequest(
        headers=request.META,
        body=request.body
    )
    response = bookings_api.register_event(api_request)
    if response['error']:
        return HttpResponse(status=400)
    return HttpResponse(status=200)


@require_http_methods(['GET'])
def generate_payment(request):
    api_request = GetBookingRequest(
        obj_id=request.GET['booking_id'],
        generate_new_session_id=True
    )
    results = bookings_api.get(api_request)
    return render(
        request,
        'pages/generate_payment.html',
        context={'session_id': results['data']['session_id']}
    )
