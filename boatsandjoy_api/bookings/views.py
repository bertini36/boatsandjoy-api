import json
from datetime import date

from django.db.models import F
from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.response import Response

from boatsandjoy_api.bookings.api import api as bookings_api
from boatsandjoy_api.bookings.models import Promocode
from boatsandjoy_api.bookings.requests import (
    CreateBookingRequest,
    GetBookingBySessionRequest,
    GetBookingRequest,
    MarkBookingAsErrorRequest,
    RegisterBookingEventRequest,
)


@api_view(["GET"])
def generate_payment(request: Request) -> Response:
    api_request = GetBookingRequest(
        obj_id=request.GET["booking_id"], generate_new_session_id=True
    )
    results = bookings_api.get(api_request)
    return Response(results)


@api_view(["POST"])
def create_booking(request: Request) -> Response:
    """
    Creates a booking

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
        base_price=data["base_price"],
        slot_ids=[int(slot_id) for slot_id in data["slot_ids"].split(",")],
        customer_name=data["customer_name"],
        customer_telephone_number=data["customer_telephone_number"],
        extras=data["extras"],
        is_resident=data["is_resident"],
        promocode=data.get("promocode"),
    )
    results = bookings_api.create(api_request)
    return Response(results)


@api_view(["POST"])
def register_booking_event(request: Request) -> Response:
    api_request = RegisterBookingEventRequest(
        headers=request.META, body=json.loads(request.body)
    )
    response = bookings_api.register_event(api_request)
    if response["error"]:
        return Response(status=400)
    return Response(status=200)


@api_view(["GET"])
def mark_booking_as_error(request: Request) -> Response:
    session_id = request.GET.get("session_id")
    results = None
    if session_id:
        api_request = MarkBookingAsErrorRequest(session_id=session_id)
        results = bookings_api.mark_as_error(api_request)
    return Response(results)


@api_view(["GET"])
def get_booking_by_session(request: Request) -> Response:
    session_id = request.GET.get("session_id")
    api_request = GetBookingBySessionRequest(session_id=session_id)
    results = bookings_api.get_booking_by_session(api_request)
    return Response(results)


@api_view(["GET"])
def validate_promocode(request: Request) -> Response:
    promocode = request.GET.get("promocode")
    use_day = date.today()
    booking_day = date(
        *[int(number) for number in request.GET.get("booking_day").split("-")]
    )
    try:
        promocode = Promocode.objects.get(
            name=promocode,
            use_from__lte=use_day,
            use_to__gte=use_day,
            booking_from__lte=booking_day,
            booking_to__gte=booking_day,
            number_of_uses__lt=F("limit_of_uses"),
        )
        return Response({"valid": True, "factor": promocode.factor})
    except Promocode.DoesNotExist:
        return Response({"valid": False})
