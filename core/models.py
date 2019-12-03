from django.contrib.auth.models import AbstractUser, UserManager
from django.db                  import models
from core.managers              import CityManager
from math                       import pi, sqrt, sin, cos, atan2
from datetime                   import date, timedelta
from django.core.exceptions     import PermissionDenied

# mixin

class HasContact(models.Model):
    class Meta:
        abstract = True
    
    _phone = models.CharField(max_length=30, db_column='phone', blank=True, null=True)
    _email = models.CharField(max_length=30, db_column='cemail', blank=True, null=True)


# abstract

class BaseModel(models.Model):
    objects         = models.Manager()
    name            = models.CharField(max_length=255, unique=False, null=True, blank=True)
    creation_date   = models.DateTimeField(auto_now_add=True, blank=True, null=True, editable=False)
    last_modified   = models.DateTimeField(auto_now=True, blank=False, null=True, editable=False)

    def __str__(self):
        return str(self.name)
    
    class Meta:
        abstract = True


class BaseUserModel(AbstractUser):
    def __str__(self):
        return str(self.username)

    class Meta:
        abstract = True
        

# models and managers

class Country(models.Model):
    name = models.CharField(max_length=64, unique=True,  null=True, blank=True)
    iso  = models.CharField(max_length=2,  unique=False, null=True, blank=True)
    
    def __str__(self):
        return str(self.name)


class City(models.Model):
    name        = models.CharField(max_length=64, unique=False, null=True, blank=True)
    country     = models.ForeignKey(Country, on_delete=models.SET_NULL, null=True, blank=True, related_name='city')
    population  = models.IntegerField(unique=False, null=True, blank=True)
    latitude    = models.FloatField(unique=False, null=True, blank=True)
    longitude   = models.FloatField(unique=False, null=True, blank=True)
    objects     = CityManager()
    
    def __str__(self):
        return str(self.name)
    
    # returns distance between two sets of coordinates in KM
    def distance(self, longitude, latitude):
        lat1  = latitude
        long1 = longitude
        lat2  = self.latitude
        long2 = self.longitude

        degree_to_rad = float (pi / 180.0)

        d_lat = (lat2 - lat1) * degree_to_rad
        d_long = (long2 - long1) * degree_to_rad

        a = pow (sin (d_lat / 2), 2) + cos (lat1 * degree_to_rad) * cos (lat2 * degree_to_rad) * pow (sin (d_long / 2), 2)
        c = 2 * atan2 (sqrt (a), sqrt (1 - a))
        return 6367 * c

    def distance_city(self, city):
        return self.distance(city.longitude, city.latitude)


# class CUserManager(UserManager):
#     def create(self, username=None, password=None):
#         # username = kwargs.pop('email', '')
#         # password = kwargs.pop('password', '')
#
#         if not username:
#             raise ValueError("Username must be provided to create user")
#
#         user = self.model(username=username)
#         # if created:
#         #     user.username = username
#         if password:
#             # set password if provided
#             user.set_password(password)
#         user.save()
#         return user


class User(BaseUserModel, HasContact):
    objects = UserManager()


class JourneyManager(models.Manager):
    @staticmethod
    def filter_date(qs, **kwargs):
        d = kwargs['date']  # date
        t = timedelta(days=kwargs['date_tolerance'])  # number of tolerance days
        min, max = (d-t, d+t)
        return [x for x in qs if x.date >= min and x.date <= max]

    @staticmethod
    def filter_city(qs, city_id, s='origin', radius=0):
        d = 3
        city = City.objects.get(id=city_id)
        if radius:
            return [x for x in qs if getattr(x, s, None).distance(longitude=city.longitude, latitude=city.latitude) < radius], city
        else:
            kwargs = {
                f'{s}__longitude__gt': city.longitude - d, f'{s}__longitude__lt': city.longitude + d,
                f'{s}__latitude__gt' : city.latitude  - d, f'{s}__latitude__lt':  city.latitude  + d
            }
            return qs.filter(**kwargs), city
    
    def all_ordered(self, **kwargs):
        if 'user' in kwargs: qs = self.filter(user=kwargs['user'])
        else : qs = self.get_queryset()
        radius = kwargs.pop('radius', 50)
        c1 = None
        c2 = None
        if 'date' in kwargs:          qs = self.filter_date(qs, **kwargs)
        if 'origin' in kwargs:        qs, c1 = self.filter_city(qs, kwargs['origin'],         s='origin',       radius=radius)
        if 'destination' in kwargs:   qs, c2 = self.filter_city(qs, kwargs['destination'],    s='destination',  radius=radius)
        if c1 and c2: qs = sorted(qs, key=lambda a: a.origin.distance(c1.longitude, c1.latitude) + a.destination.distance(c2.longitude, c2.latitude))
        return qs
    
    # def create(self, name=None, origin=None, destination=None, user=None, date=None):
    def create(self, **kwargs):
        if kwargs['user'] is None or kwargs['user'].is_anonymous:
            raise PermissionDenied('Please log in to add a journey.')
        journey_obj = self.model()
        for kwarg in kwargs:
            setattr(journey_obj, kwarg, kwargs[kwarg])
        journey_obj.save()
        return journey_obj


class Journey(BaseModel, HasContact):
    name         = models.CharField(max_length=255, unique=False, null=True, blank=True)
    origin       = models.ForeignKey(City, on_delete=models.SET_NULL, null=True, blank=True, related_name='journey_origin')
    destination  = models.ForeignKey(City, on_delete=models.SET_NULL, null=True, blank=True, related_name='journey_destination')
    user         = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='journey')
    date         = models.DateField(null=True, blank=True)
    objects      = JourneyManager()

    @property
    def _destination(self):
        return str(self.destination)
        
    @_destination.setter
    def _destination(self, value):
        self.destination = City.objects.get_json(value)

    @property
    def _origin(self):
        return  str(self.origin)

    @_origin.setter
    def _origin(self, value):
        self.origin = City.objects.get_json(value)
    
    
    @property
    def phone(self):
        if self._phone: return self._phone
        return self.user._phone
    
    @phone.setter
    def phone(self, value):
        self._phone = value
        
    @property
    def email(self):
        if self._email: return self._email
        return self.user._email
    
    @email.setter
    def email(self, value):
        self._email = value

    
    def __str__(self):
        return f'{str(self.name)}: from {str(self.origin)} to {str(self.destination)}'
