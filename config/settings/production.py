import django_heroku
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

from .base import *

# DJANGO HEROKU
# https://github.com/heroku/django-heroku
# ------------------------------------------------------------------------------
django_heroku.settings(locals())

# APP CONFIGURATION
# ******************************************************************************

# DEBUG
# https://docs.djangoproject.com/en/dev/ref/settings/#debug
# ------------------------------------------------------------------------------
DEBUG = False

# SITE CONFIGURATION
# https://docs.djangoproject.com/en/1.6/ref/settings/#allowed-hosts
# ------------------------------------------------------------------------------
ALLOWED_HOSTS = ("boatsandjoy-api.herokuapp.com",)

# TEMPLATE CONFIGURATION
# https://docs.djangoproject.com/en/dev/ref/templates/api/#django.template.loaders.cached.Loader
# ------------------------------------------------------------------------------
TEMPLATES[0]["OPTIONS"]["loaders"] = [
    (
        "django.template.loaders.cached.Loader",
        [
            "django.template.loaders.filesystem.Loader",
            "django.template.loaders.app_directories.Loader",
        ],
    ),
]

# LOGGING
# https://docs.djangoproject.com/en/dev/topics/logging/
# ------------------------------------------------------------------------------
LOGGING = {
    "version": 1,
    "disable_existing_loggers": True,
    "formatters": {
        "verbose": {
            "format": "%(levelname)-7s %(asctime)s %(message)s",
            "datefmt": "%d-%m-%Y %H:%M:%S",
        },
    },
    "handlers": {
        "file": {
            "level": "DEBUG",
            "class": "logging.FileHandler",
            "filename": BASE_DIR("logs/boatsandjoy_api.log"),
            "formatter": "verbose",
        },
    },
    "loggers": {
        "django": {
            "handlers": ["file"],
            "propagate": True,
            "level": "DEBUG",
        },
        "boatsandjoy_api": {
            "handlers": ["file"],
            "level": "DEBUG",
        },
    },
}

# SENTRY
# https://docs.sentry.io/platforms/python/django
sentry_sdk.init(
    dsn=env("SENTRY_DSN"),
    integrations=[DjangoIntegration()],
    environment="prod",
    send_default_pii=True,
)

# SECURE SSL
# ------------------------------------------------------------------------------
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_SSL_REDIRECT = True
