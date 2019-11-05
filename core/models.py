from django.contrib.auth.models import AbstractUser
from django.db                  import models
from core.managers              import CityManager
from math                       import pi, sqrt, sin, cos, atan2


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

    # def distance2(self, city1, city2):
    #     return self.distance(city1.longitude, city1.latitude) + self.distance(city2.longitude, city2.latitude)
from datetime import date, timedelta
class JourneyManager(models.Manager):
    @staticmethod
    def filter_date(qs, **kwargs):
        date_range = [date.today() - timedelta(days=1), date.today() + timedelta(days=1)]
        return [x for x in qs if x.date >= date_range[0] and x.date <= date_range[1]]

    @staticmethod
    def filter_city(qs, city_id, s='origin', radius=0):
        d = 3
        city = City.objects.get(id=city_id)
        if radius:
            return [x for x in qs if getattr(x, s, None).distance(longitude=city.longitude, latitude=city.latitude) < radius]
        else:
            kwargs = {
                f'{s}__longitude__gt': city.longitude - d, f'{s}__longitude__lt': city.longitude + d,
                f'{s}__latitude__gt' : city.latitude  - d, f'{s}__latitude__lt':  city.latitude  + d
            }
            return qs.filter(**kwargs), city
    

    def all_ordered(self, **kwargs):
        qs = self.get_queryset ()
        radius = kwargs.pop('radius', 0)
        c1 = None
        c2 = None
        if 'date' in kwargs:          qs = self.filter_date(qs, **kwargs)
        if 'origin' in kwargs:        qs, c1 = self.filter_city(qs, kwargs['origin'],         s='origin',       radius=radius)
        if 'destination' in kwargs:   qs, c2 = self.filter_city(qs, kwargs['destination'],    s='destination',  radius=radius)
        if c1 and c2: qs = sorted(qs, key=lambda a: a.origin.distance(c1.longitude, c1.latitude) + a.destination.distance(c2.longitude, c2.latitude))
        return qs


class Journey(BaseModel):
    name        = models.CharField(max_length=255, unique=False, null=True, blank=True)
    origin      = models.ForeignKey(City, on_delete=models.SET_NULL, null=True, blank=True, related_name='journey_origin')
    destination = models.ForeignKey(City, on_delete=models.SET_NULL, null=True, blank=True, related_name='journey_destination')
    date        = models.DateField(null=True, blank=True)
    objects     = JourneyManager()
    
    def __str__(self):
        return f'{str(self.name)}: from {str(self.origin)} to {str(self.destination)}'
    
    
# class Shipment_dep(BaseModel):
#     journey  = models.ForeignKey(Journey, on_delete=models.SET_NULL, null=True, blank=True, related_name='shipment')


class User(BaseUserModel):
    journeys = models.ManyToManyField(Journey)
