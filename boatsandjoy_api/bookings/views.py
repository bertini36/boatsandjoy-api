import json
from datetime import date

from django.db.models import F
from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.response import Response

from boatsandjoy_api.bookings.api import api as bookings_api
from boatsandjoy_api.bookings.factories import build_bookings_service
from boatsandjoy_api.bookings.models import Booking, Promocode
from boatsandjoy_api.bookings.requests import (
    CreateBookingRequest,
    GetBookingBySessionRequest,
    MarkBookingAsErrorRequest,
)


@api_view(["POST"])
def create_booking(request: Request) -> Response:
    """
    Creates a booking

    :returns {
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
    request = CreateBookingRequest(
        base_price=data["base_price"],
        slot_ids=[int(slot_id) for slot_id in data["slot_ids"].split(",")],
        customer_name=data["customer_name"],
        customer_telephone_number=data["customer_telephone_number"],
        extras=data["extras"],
        is_resident=data["is_resident"],
        promocode=data.get("promocode"),
    )
    service = build_bookings_service()
    booking = service.create(request)
    return Response(booking)


@api_view(["GET"])
def force_booking_checkout(request: Request) -> Response:
    booking = Booking.objects.get(id=request.GET["booking_id"])
    service = build_bookings_service()
    booking = service.force_checkout(booking)
    return Response(booking)


@api_view(["POST"])
def register_payment(request: Request) -> Response:
    service = build_bookings_service()
    service.register_payment(json.loads(request.body))
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
