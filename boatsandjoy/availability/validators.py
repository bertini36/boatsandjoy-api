# coding: utf-8

from django import forms

from boatsandjoy.core.validators import DjangoRequestValidator


class DjangoGetAvailabilityForm(forms.Form):
    date = forms.DateField(required=True)
    apply_resident_discount = forms.BooleanField(required=False)


class GetAvailabilityRequestValidator(DjangoRequestValidator):
    FORM = DjangoGetAvailabilityForm


class DjangoGetMonthAvailabilityForm(forms.Form):
    month = forms.IntegerField(required=True)
    year = forms.IntegerField(required=True)


class GetMonthAvailabilityRequestValidator(DjangoRequestValidator):
    FORM = DjangoGetMonthAvailabilityForm
