from django.http import HttpRequest, JsonResponse
from django.views.decorators.http import require_http_methods

from boatsandjoy_api.core.utils import transform_to_internal_date
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
