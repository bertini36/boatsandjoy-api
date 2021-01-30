# -*- coding: UTF-8 -*-

from django.utils.translation import gettext_lazy as _

TRANSLATIONS = {
    'DATE_REQUIRED': _('You have to select a date'),
    'NO_AVAILABILITY': _('There are no availAbility for this day'),
    'PAYMENT_ERROR': _(
        'It seems that there was an error redirecting to the payment gateway'
    ),
    'PRICING_OPTION_REQUIRED': _('You have to select a pricing option'),
    'LEGAL_ADVICE_HAS_TO_BE_ACCEPTED': _('Legal advice has to be accepted'),
    'TERMS_AND_CONDITIONS_HAVE_TO_BE_ACCEPTED': _(
        'Terms and conditions have to be accepted'
    ),
    'CLIENT_NAME_IS_REQUIRED': _('You have to introduce your name')
}
