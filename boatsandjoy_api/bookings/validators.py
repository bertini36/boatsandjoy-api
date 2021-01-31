from django import forms

from boatsandjoy_api.core.utils import MultipleIntField
from boatsandjoy_api.core.validators import DjangoRequestValidator


class DjangoBookingCreationForm(forms.Form):
    price = forms.DecimalField(required=True)
    slot_ids = MultipleIntField(required=True)
    customer_name = forms.CharField(required=True)
    customer_telephone_number = forms.CharField(required=False)


class DjangoGetBookingForm(forms.Form):
    obj_id = forms.IntegerField(required=True)


class BookingCreationRequestValidator(DjangoRequestValidator):
    FORM = DjangoBookingCreationForm


class GetBookingRequestValidator(DjangoRequestValidator):
    FORM = DjangoGetBookingForm


class DjangoIdentifyBookingBySessionForm(forms.Form):
    session_id = forms.CharField(required=True)


class IdentifyBookingBySessionRequestValidator(DjangoRequestValidator):
    FORM = DjangoIdentifyBookingBySessionForm
