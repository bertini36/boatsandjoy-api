from boatsandjoy_api.core.exceptions import BoatsAndJoyException


class BoatNotFound(BoatsAndJoyException):
    pass


class NoActiveBoat(BoatsAndJoyException):
    pass
