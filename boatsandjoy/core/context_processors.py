# -*- coding: utf-8 -*-

from django.conf import settings


def common(request):
    return {
        'DEBUG': settings.DEBUG,
        'STRIPE_API_KEY': settings.STRIPE_API_KEY,
        'GOOGLE_API_KEY': settings.GOOGLE_API_KEY,
        'HARBOUR_LOCATION': settings.HARBOUR_LOCATION
    }

