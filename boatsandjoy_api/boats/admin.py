from django.contrib import admin, messages
from django.contrib.admin.helpers import ActionForm
from django.db.models import QuerySet
from django.forms import ValidationError
from django.forms.fields import CharField
from django.forms.models import BaseInlineFormSet
from django.http import HttpRequest
from django.urls import reverse
from django.utils.safestring import mark_safe

from boatsandjoy_api.availability.availability_generators import (
    AvailabilityGenerator,
)
from boatsandjoy_api.availability.domain import DateRange
from boatsandjoy_api.availability.models import (
    Day,
    DayDefinition,
    PriceVariation,
)
from boatsandjoy_api.availability.utils import date_ranges_collision
from boatsandjoy_api.core.exceptions import BoatsAndJoyException
from .models import Boat


class DayDefinitionInlineFormset(BaseInlineFormSet):
    def clean(self):
        for i, day_definition1 in enumerate(self.cleaned_data):
            for j, day_definition2 in enumerate(self.cleaned_data):
                if day_definition2['from_date'] > day_definition2['to_date']:
                    raise ValidationError(
                        f'Some day definition has its from '
                        f'date greater than its to date'
                    )
                if i != j:
                    if date_ranges_collision(
                        DateRange(
                            from_date=day_definition1['from_date'],
                            to_date=day_definition1['to_date'],
                        ),
                        DateRange(
                            from_date=day_definition2['from_date'],
                            to_date=day_definition2['to_date'],
                        ),
                    ):
                        raise ValidationError(
                            f'Exists a collision between the '
                            f'date ranges of some day definitions'
                        )
        return self.cleaned_data


class DayDefinitionInlineAdmin(admin.StackedInline):
    model = DayDefinition
    formset = DayDefinitionInlineFormset
    extra = 0

    def has_delete_permission(
        self, request: HttpRequest, obj: Day = None
    ) -> bool:
        return False


class PriceVariationInlineFormset(BaseInlineFormSet):
    def clean(self):
        for i, price_variation1 in enumerate(self.cleaned_data):
            for j, price_variation2 in enumerate(self.cleaned_data):
                if (
                    'from_date' not in price_variation2
                    or 'to_date' not in price_variation2
                    or 'from_date' not in price_variation1
                    or 'to_date' not in price_variation1
                ):
                    raise ValidationError(
                        'Some price variations have not '
                        'all its required data filled'
                    )
                if price_variation2['from_date'] > price_variation2['to_date']:
                    raise ValidationError(
                        f'Some price definition has its from '
                        f'date greater than its to date'
                    )
                if i != j:
                    if date_ranges_collision(
                        DateRange(
                            from_date=price_variation1['from_date'],
                            to_date=price_variation1['to_date'],
                        ),
                        DateRange(
                            from_date=price_variation2['from_date'],
                            to_date=price_variation2['to_date'],
                        ),
                    ):
                        raise ValidationError(
                            f'Exists a collision between the '
                            f'date ranges of some price variations'
                        )
        return self.cleaned_data


class PriceVariationInlineAdmin(admin.StackedInline):
    model = PriceVariation
    formset = PriceVariationInlineFormset
    extra = 0


def generate_availability_for(
    modeladmin, request: HttpRequest, queryset: QuerySet
):
    try:
        year = int(request.POST['year'])
        if not year:
            raise ValueError
    except ValueError:
        messages.add_message(
            request, messages.ERROR, 'You have to specify a year'
        )
        return
    for boat in queryset:
        try:
            availability_generator = AvailabilityGenerator(boat)
            availability_generator.generate(year)
        except BoatsAndJoyException as e:
            messages.add_message(
                request,
                messages.ERROR,
                f'Unable to generate availability for boat {boat} because {e}',
            )


generate_availability_for.short_description = 'Generate availability for year'


def delete_availability_for(
    modeladmin, request: HttpRequest, queryset: QuerySet
):
    try:
        year = int(request.POST['year'])
        if not year:
            raise Exception
    except Exception:
        messages.add_message(
            request, messages.ERROR, 'You have to specify a year'
        )
        return
    for boat in queryset:
        try:
            availability_generator = AvailabilityGenerator(boat)
            availability_generator.delete(year)
        except BoatsAndJoyException as e:
            messages.add_message(
                request,
                messages.ERROR,
                f'Unable to delete availability for boat {boat} because {e}',
            )


delete_availability_for.short_description = 'Delete availability for year'


def deactivate_selected_boats(
    modeladmin, request: HttpRequest, queryset: QuerySet
):
    queryset.update(active=False)


deactivate_selected_boats.short_description = 'Deactivate selected boats'


class BoatAdminActionForm(ActionForm):
    year = CharField(required=False)


class BoatAdmin(admin.ModelAdmin):
    list_filter = ('active', 'name', 'created')
    list_display = (
        'active',
        'get_name_link',
        'get_created_date',
        'get_availability_link',
    )
    inlines = (
        DayDefinitionInlineAdmin,
        PriceVariationInlineAdmin,
    )
    action_form = BoatAdminActionForm
    actions = [
        generate_availability_for,
        delete_availability_for,
        deactivate_selected_boats,
    ]

    def get_name_link(self, obj: Boat) -> str:
        url = reverse(
            f'admin:{obj._meta.app_label}_{obj._meta.model_name}_change',
            args=[obj.id],
        )
        return mark_safe(f'<a href="{url}">{obj.name}</a>')

    def get_created_date(self, obj: Boat) -> str:
        url = reverse(
            f'admin:{obj._meta.app_label}_{obj._meta.model_name}_change',
            args=[obj.id],
        )
        return mark_safe(f'<a href="{url}">{obj.created}</a>')

    def get_availability_link(self, obj: Boat) -> str:
        url = reverse(f'admin:availability_day_changelist')
        url += f'?definition__boat__id__exact={obj.id}'
        return mark_safe(
            f'<a href="{url}" target="_blank">Check availability</a>'
        )


admin.site.register(Boat, BoatAdmin)
