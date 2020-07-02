# coding: utf-8

from django import forms

from boatsandjoy.core.validators import DjangoRequestValidator


class DjangoFilterBoatsForm(forms.Form):
    name = forms.CharField(required=False)
    active = forms.BooleanField(required=False)


class FilterBoatsRequestValidator(DjangoRequestValidator):
    FORM = DjangoFilterBoatsForm


