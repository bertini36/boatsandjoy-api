# -*- coding: UTF-8 -*-

from boatsandjoy.core.exceptions import BoatsAndJoyException


class BoatsApiException(BoatsAndJoyException):
    pass


class BoatNotFound(BoatsApiException):
    pass


class NoActiveBoat(BoatsApiException):
    pass
