from django.apps import AppConfig

from suit.apps import DjangoSuitConfig


class CoreConfig(AppConfig):
    name = 'boatsandjoy_api.core'
    verbose_name = 'Core'


class SuitConfig(DjangoSuitConfig):
    layout = 'horizontal'
