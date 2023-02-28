from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass

from .exceptions import InvalidDataError


class RequestValidatorInterface(ABC):
    """
    This validators are used to validate api requests types and if are required
    """

    @classmethod
    @abstractmethod
    def validate(cls, params: any):
        pass


class DjangoRequestValidator(RequestValidatorInterface):
    FORM = None

    @classmethod
    def validate(cls, request: dataclass):
        form = cls.FORM(data=asdict(request))
        if not form.is_valid():
            raise InvalidDataError(f"Validation error {form.errors.as_text()}")
