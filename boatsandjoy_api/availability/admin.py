from typing import List

from django.contrib import admin
from django.contrib.admin import SimpleListFilter
from django.db.models import QuerySet
from django.http import HttpRequest
from django.urls import reverse
from django.utils.safestring import mark_safe

from .constants import Months
from .models import Day, Slot


class SlotInlineAdmin(admin.StackedInline):
    model = Slot
    extra = 0
    exclude = ("position",)

    def has_delete_permission(self, request, obj: Slot = None) -> bool:
        return False


def get_days(
    queryset: QuerySet = None, year: int = None, month: int = None
) -> QuerySet:
    if not queryset:
        queryset = Day.objects.all()
    if year:
        queryset = queryset.filter(date__year__lte=year, date__year__gte=year)
    if month:
        queryset = queryset.filter(date__month__lte=month, date__month__gte=month)
    return queryset


class MonthFilter(SimpleListFilter):
    title = "month"
    parameter_name = "month"

    def lookups(self, request: HttpRequest, model_admin) -> List[tuple]:
        return Months.LIST

    def queryset(self, request, queryset: QuerySet) -> QuerySet:
        month = self.value()
        if month:
            return get_days(queryset=queryset, month=month)


class YearFilter(SimpleListFilter):
    title = "year"
    parameter_name = "year"

    def lookups(self, request: HttpRequest, model_admin) -> List[tuple]:
        return [("2019", "2019"), ("2020", "2020"), ("2021", "2021")]

    def queryset(self, request: HttpRequest, queryset: QuerySet) -> QuerySet:
        year = self.value()
        if year:
            return get_days(queryset=queryset, year=year)


class DayAdmin(admin.ModelAdmin):
    list_filter = ("definition__boat", MonthFilter, YearFilter)
    list_display = ("get_boat_link", "get_date_link", "get_slots")
    inlines = (SlotInlineAdmin,)

    def has_add_permission(self, request: HttpRequest, obj: Day = None) -> bool:
        return False

    def get_actions(self, request: HttpRequest) -> List[str]:
        actions = super().get_actions(request)
        if "delete_selected" in actions:
            del actions["delete_selected"]
        return actions

    def get_slots(self, obj: Day) -> str:
        slots_html = ""
        url = reverse(
            f"admin:{obj._meta.app_label}_{obj._meta.model_name}_change",
            args=[obj.id],
        )
        for slot in obj.slots.all():
            if slot.booked:
                slots_html += (
                    f'<a href="{url}">'
                    '<img src="/static/admin/img/icon-no.svg" alt="False">'
                    "</a>"
                )
            else:
                slots_html += (
                    f'<a href="{url}">'
                    '<img src="/static/admin/img/icon-yes.svg" alt="True">'
                    "</a>"
                )
        return mark_safe(slots_html)

    get_slots.short_description = "Available slots"

    def get_readonly_fields(self, request: HttpRequest, obj: Day = None) -> List[str]:
        return ["definition", "date"]

    def get_boat_link(self, obj: Day) -> str:
        url = reverse(f"admin:boats_boat_change", args=[obj.boat.id])
        return mark_safe(f'<a href="{url}" target="_blank">{obj.boat}</a>')

    get_boat_link.short_description = "Boat"

    def get_date_link(self, obj: Day) -> str:
        url = reverse(
            f"admin:{obj._meta.app_label}_{obj._meta.model_name}_change",
            args=[obj.id],
        )
        return mark_safe(f'<a href="{url}">{obj.date}</a>')

    get_date_link.short_description = "Date"


admin.site.register(Day, DayAdmin)
