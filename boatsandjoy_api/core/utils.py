from datetime import date, datetime

from django import forms
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string


def filter_none_values_in_dict(dict_):
    return dict((k, v) for k, v in dict_.items() if v is not None)


def cast_to_date(obj: str) -> date:
    return datetime.strptime(obj, settings.DATE_FORMAT).date()


class MultipleIntField(forms.TypedMultipleChoiceField):
    def __init__(self, *args, **kwargs):
        super(MultipleIntField, self).__init__(*args, **kwargs)
        self.coerce = int

    def valid_value(self, value):
        return True


def send_email(subject: str, to_email: str, template: str, **kwargs):
    msg = EmailMultiAlternatives(
        subject=subject, from_email=settings.DEFAULT_FROM_EMAIL, to=[to_email]
    )
    msg.attach_alternative(render_to_string(template, kwargs), "text/html")
    msg.send()
