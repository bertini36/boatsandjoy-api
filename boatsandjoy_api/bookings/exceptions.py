from boatsandjoy_api.core.exceptions import BoatsAndJoyException


class BookingsApiException(BoatsAndJoyException):
    pass


class BookingInvalidDataError(BookingsApiException):
    pass


class NoSlotsSelected(BookingsApiException):
    pass


class BookingNotFound(BookingsApiException):
    pass


class BookingAlreadyConfirmed(BookingsApiException):
    pass


class BookingAlreadyPending(BookingsApiException):
    pass
