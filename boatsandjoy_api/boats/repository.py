from abc import ABC, abstractmethod
from typing import List

from django.conf import settings
from django.utils.translation import gettext_lazy as _

from boatsandjoy_api.core.data_adapters import DjangoDataAdapter
from . import domain, models
from .exceptions import BoatNotFound


class BoatsRepository(ABC):

    @classmethod
    @abstractmethod
    def filter(
        cls,
        obj_id: int = None,
        name: str = None,
        active: bool = None
    ) -> List[domain.Boat]:
        pass

    @classmethod
    @abstractmethod
    def get(
        cls,
        obj_id: int = None,
        name: str = None,
        active: bool = None
    ) -> domain.Boat:
        pass


class DjangoBoatsRepository(BoatsRepository):
    DATA_ADAPTER = DjangoDataAdapter

    @classmethod
    def filter(
        cls,
        obj_id: int = None,
        name: str = None,
        active: bool = None
    ) -> List[domain.Boat]:
        django_filters = cls.DATA_ADAPTER.transform(
            obj_id=obj_id,
            name=name,
            active=active
        )
        boats = models.Boat.objects.filter(**django_filters)
        return [cls.get_boat_domain_object(boat) for boat in boats]

    @classmethod
    def get(
        cls,
        obj_id: int = None,
        name: str = None,
        active: bool = None
    ) -> domain.Boat:
        django_filters = cls.DATA_ADAPTER.transform(
            obj_id=obj_id,
            name=name,
            active=active
        )
        try:
            boat = models.Boat.objects.get(**django_filters)
        except models.Boat.DoesNotExist as e:
            raise BoatNotFound(_(f'Boat not found: {e}'))
        return cls.get_boat_domain_object(boat)

    @classmethod
    def get_boat_domain_object(cls, boat: models.Boat) -> domain.Boat:
        photos = [
            domain.Photo(
                url=f'{settings.MEDIA_URL}{partial_url}',
                description=description
            )
            for partial_url, description in boat.photos.values_list(
                'image',
                'description'
            )
        ]
        return domain.Boat(
            id=boat.id,
            created=boat.created,
            name=boat.name,
            description=boat.description,
            active=boat.active,
            photos=photos
        )
