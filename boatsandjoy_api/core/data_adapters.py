from abc import ABC, abstractmethod
from copy import deepcopy

from .utils import filter_none_values_in_dict


class DataAdapterInterface(ABC):
    @classmethod
    @abstractmethod
    def transform(cls, **kwargs) -> dict:
        pass


class DjangoDataAdapter(DataAdapterInterface):
    @classmethod
    def transform(cls, **kwargs) -> dict:
        django_data = filter_none_values_in_dict(deepcopy(kwargs))
        if 'obj_id' in django_data:
            django_data['id'] = django_data.pop('obj_id')
        return django_data
