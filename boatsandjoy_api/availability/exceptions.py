# -*- coding: UTF-8 -*-

from boatsandjoy_api.core.exceptions import BoatsAndJoyException


class AvailabilityApiException(BoatsAndJoyException):
    pass


class NoDayDefinitionDefined(AvailabilityApiException):
    pass


class NoAvailabilityForDay(AvailabilityApiException):
    pass


class CombinationOfSize0(AvailabilityApiException):
    pass


class NoSameDaySlots(AvailabilityApiException):
    pass


class NoSlotsAvailable(AvailabilityApiException):
    pass


class AvailabilityAlreadyCreated(AvailabilityApiException):
    pass
