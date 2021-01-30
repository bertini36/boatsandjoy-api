from abc import ABC, abstractmethod
from datetime import date

from boatsandjoy_api.core.utils import format_date


class ResponseBuilderInterface(ABC):

    def __init__(self, data: any):
        self.data = data

    @abstractmethod
    def build(self):
        pass


class ErrorResponseBuilder(ResponseBuilderInterface):

    def build(self) -> dict:
        return {'error': True, 'data': str(self.data)}


class ResponseBuilder(ResponseBuilderInterface):

    def build(self) -> dict:
        if isinstance(self.data, dict):
            data = self._serialize_dict(self.data)
        elif isinstance(self.data, list):
            data = [
                self._serialize_object(obj)
                if type(obj) != dict
                else self._serialize_dict(obj)
                for obj in self.data
            ]
        else:
            data = self._serialize_object(self.data)
        return {'error': False, 'data': data}

    def _serialize_dict(self, dict_obj: dict) -> dict:
        return self._cast_dict_attrs(dict_obj)

    @staticmethod
    def _cast_dict_attrs(dict_obj: dict) -> dict:
        for key in dict_obj:
            if isinstance(dict_obj[key], date):
                dict_obj[key] = format_date(dict_obj[key])
        return dict_obj

    def _serialize_object(self, obj: object) -> dict:
        attrs = self._get_vars(obj)
        obj = self._cast_obj_attrs(obj, attrs)
        return {
            attr: getattr(obj, attr)
            for attr in attrs
        }

    @staticmethod
    def _get_vars(data) -> list:
        if not data:
            return []
        if isinstance(data, list):
            element = data[0]
        else:
            element = data
        if type(element) == dict:
            return list(element.keys())
        return list(vars(element).keys())

    @staticmethod
    def _cast_obj_attrs(obj, attrs):
        for attr in attrs:
            if isinstance(getattr(obj, attr), date):
                setattr(obj, attr, format_date(getattr(obj, attr)))
        return obj
