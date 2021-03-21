from calendar import Calendar
from datetime import date, timedelta

from .domain import DateRange


def daterange(start_date: date, end_date: date):
    for n in range(int((end_date - start_date).days)):
        yield start_date + timedelta(n)


def date_ranges_collision(date_range_1: DateRange, date_range_2: DateRange):
    if date_range_1.from_date > date_range_2.to_date:
        return False
    if date_range_1.to_date < date_range_2.from_date:
        return False
    return True


def month_date_iter(year, month):
    calendar = Calendar()
    return [d for d in calendar.itermonthdates(year, month) if d.month == month]
