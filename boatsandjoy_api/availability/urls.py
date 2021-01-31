from django.urls import re_path

from .views import get_day_availability, get_month_availability

app_name = 'availability'

urlpatterns = [
    re_path(
        r'day/(?P<date_>\d{4}-\d{2}-\d{2})/',
        get_day_availability,
        name='get-day-availability',
    ),
    re_path(
        r'month/(?P<date_>\d{4}-\d{2}-\d{2})/',
        get_month_availability,
        name='get-month-availability',
    ),
]
