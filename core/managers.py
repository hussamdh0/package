from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models


class CityManager(models.Manager):
    def all_ordered(self, **kwargs):
        qs = self.get_queryset()
        if ('longitude' in kwargs and 'latitude' in kwargs):
            return sorted(qs, key=lambda a: a.distance(**kwargs))
        if ('longitude' in kwargs):
            qs = qs.filter(longitude__gt=kwargs['longitude'] - 3, longitude__lt=kwargs['longitude'] + 3)
        if ('latitude' in kwargs):
            qs = qs.filter(latitude__gt= kwargs['latitude']  - 3, latitude__lt= kwargs['latitude']  + 3)
        return qs.order_by('-population')
    
    def get_json(self, value):
        if type(value) is int:
            return self.get(id=value)
        if type(value) is str:
            qs = self.filter(name__iexact=value)
            res = None
            if len(qs) == 1:
                res = qs[0]
            if len(qs) >  1:
                res = qs[0]
                for e in qs[1:]:
                    if e.population > res.population:
                        res = e
            return res