from dataclasses import asdict
from typing import Type

from boatsandjoy_api.core.responses import (
    ErrorResponseBuilder,
    ResponseBuilder,
    ResponseBuilderInterface,
)
from .exceptions import BoatsApiException
from .repository import BoatsRepository, DjangoBoatsRepository
from .requests import FilterBoatsRequest
from .validators import FilterBoatsRequestValidator


class BoatsApi:
    def __init__(
        self,
        boats_repository: Type[BoatsRepository],
        response_builder: Type[ResponseBuilderInterface],
        error_builder: Type[ResponseBuilderInterface],
    ):
        self.boats_repository = boats_repository
        self.response_builder = response_builder
        self.error_builder = error_builder

    def filter(self, request: FilterBoatsRequest) -> dict:
        try:
            FilterBoatsRequestValidator.validate(request)
            boats = self.boats_repository.filter(**asdict(request))
            return self.response_builder(boats).build()

        except BoatsApiException as e:
            return self.error_builder(e).build()

    def get(self, request: FilterBoatsRequest) -> dict:
        try:
            FilterBoatsRequestValidator.validate(request)
            boat = self.boats_repository.get(**asdict(request))
            return self.response_builder(boat).build()

        except BoatsApiException as e:
            return self.error_builder(e).build()


api = BoatsApi(DjangoBoatsRepository, ResponseBuilder, ErrorResponseBuilder)
