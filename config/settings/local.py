import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

from .base import *

# APP CONFIGURATION
# ******************************************************************************

# DEBUG
# https://docs.djangoproject.com/en/dev/ref/settings/#debug
# ------------------------------------------------------------------------------
DEBUG = True

# TEMPLATES
# ------------------------------------------------------------------------------
TEMPLATES[0]['OPTIONS']['debug'] = DEBUG

# ALLOWED HOSTS
# https://docs.djangoproject.com/en/dev/ref/settings/#allowed-hosts
# ------------------------------------------------------------------------------
ALLOWED_HOSTS = ['*']

# LOGGING
# https://docs.djangoproject.com/en/dev/topics/logging/
# ------------------------------------------------------------------------------
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '%(levelname)-7s %(asctime)s %(message)s',
            'datefmt': '%d-%m-%Y %H:%M:%S',
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'boatsandjoy_api': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
    },
}

# THIRD PARTY APPLICATIONS
# ******************************************************************************

# DJANGO DEBUG TOOLBAR
# https://github.com/jazzband/django-debug-toolbar
# ------------------------------------------------------------------------------
INSTALLED_APPS += ('debug_toolbar',)
MIDDLEWARE += ('debug_toolbar.middleware.DebugToolbarMiddleware',)
INTERNAL_IPS = [
    '127.0.0.1',
]

# Django-extensions
# https://github.com/django-extensions/django-extensions
# ------------------------------------------------------------------------------
INSTALLED_APPS += ('django_extensions',)

# SENTRY
# https://docs.sentry.io/platforms/python/django
sentry_sdk.init(
    dsn=env('SENTRY_DSN'),
    integrations=[DjangoIntegration()],
    environment='pre',
    send_default_pii=True,
)
