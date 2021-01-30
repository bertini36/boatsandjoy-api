from django.http import HttpRequest, JsonResponse
from django.views.decorators.http import require_http_methods

from boatsandjoy_api.core.utils import cast_to_date
from .api import api as availability_api
from .requests import GetDayAvailabilityRequest, GetMonthAvailabilityRequest


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
    date_ = cast_to_date(date_)
    apply_resident_discount = get_apply_resident_discount(request)
    api_request = GetDayAvailabilityRequest(
        date=date_,
        apply_resident_discount=apply_resident_discount
    )
    results = availability_api.get_day_availability(api_request)
    return JsonResponse(results)


def get_apply_resident_discount(request: HttpRequest) -> bool:
    if 'apply_resident_discount' in request.GET:
        return bool(int(request.GET['apply_resident_discount']))
    return False


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
    date_ = cast_to_date(date_)
    api_request = GetMonthAvailabilityRequest(
        month=date_.month,
        year=date_.year
    )
    results = availability_api.get_month_availability(request=api_request)
    return JsonResponse(results)
