from django.db.models import QuerySet


class BoatQuerySet(QuerySet):
    def active(self):
        return self.filter(active=True)
