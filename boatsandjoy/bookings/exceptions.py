# -*- coding: UTF-8 -*-

from boatsandjoy.core.exceptions import BoatsAndJoyException


class BookingsApiException(BoatsAndJoyException):
    pass


class BookingInvalidDataError(BookingsApiException):
    pass


class NoSlotsSelected(BookingsApiException):
    pass


class BookingNotFound(BookingsApiException):
    pass


class PaymentGatewayException(BookingsApiException):
    pass


class BookingAlreadyConfirmed(BookingsApiException):
    pass


class BookingAlreadyPending(BookingsApiException):
    pass


