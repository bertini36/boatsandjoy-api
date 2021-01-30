from boatsandjoy_api.core.exceptions import BoatsAndJoyException


class BoatsApiException(BoatsAndJoyException):
    pass


class BoatNotFound(BoatsApiException):
    pass


class NoActiveBoat(BoatsApiException):
    pass
