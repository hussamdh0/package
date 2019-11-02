from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models


class CityManager(models.Manager):
    # def create(self, **kwargs):
    #
    #     user = super (ApplicantManager, self).create (**kwargs)
    #     user.save ()
    #     kwargs.pop ('email', '')
    #     kwargs.pop ('password', '')
    #
    #     instance = self.model (user=user)
    #     for kwarg in kwargs:
    #         setattr (instance, kwarg, kwargs[kwarg])
    #     # instance.user = user
    #     return instance
    #
    # def get_or_create(self, *args, **kwargs):
    #     email = kwargs.pop ('email', '')
    #     password = kwargs.pop ('password', '')
    #
    #     try:
    #         instance = self.create (email=email, password=password, **kwargs)
    #
    #         return instance, True
    #     except ValidationError:
    #         instance = self.get (user__email=email)
    #
    #         return instance, False
    def all_ordered(self, **kwargs):
        qs = self.get_queryset()
        if ('longitude' in kwargs and 'latitude' in kwargs):
            return sorted(qs, key=lambda a: a.distance_squared(**kwargs))
        if ('longitude' in kwargs):
            qs = qs.filter(longitude__gt=kwargs['longitude'] - 3, longitude__lt=kwargs['longitude'] + 3)
        if ('latitude' in kwargs):
            qs = qs.filter(latitude__gt= kwargs['latitude']  - 3, latitude__lt= kwargs['latitude']  + 3)
        return qs.order_by('-population')
