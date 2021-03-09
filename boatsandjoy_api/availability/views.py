from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.response import Response

from boatsandjoy_api.core.utils import cast_to_date
from .api import api as availability_api
from .requests import GetDayAvailabilityRequest, GetMonthAvailabilityRequest


@api_view(['GET'])
def get_day_availability(request: Request, date_: str) -> Response:
    """
    Get boats day availability

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
    date_ = cast_to_date(date_)
    apply_resident_discount = get_apply_resident_discount(request)
    api_request = GetDayAvailabilityRequest(
        date=date_,
        apply_resident_discount=apply_resident_discount
    )
    results = availability_api.get_day_availability(api_request)
    return Response(results)


def get_apply_resident_discount(request: Request) -> bool:
    if 'apply_resident_discount' in request.GET:
        return bool(int(request.GET['apply_resident_discount']))
    return False


@api_view(['GET'])
def get_month_availability(request: Request, date_: str) -> Response:
    """
    Get boats month availability

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
    date_ = cast_to_date(date_)
    api_request = GetMonthAvailabilityRequest(
        month=date_.month,
        year=date_.year
    )
    results = availability_api.get_month_availability(request=api_request)
    return Response(results)
