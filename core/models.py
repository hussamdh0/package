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
        # a = longitude - self.longitude
        b = latitude  - self.latitude
        # return a ** 2 + b ** 2
        
        lat1  = latitude
        long1 = longitude
        lat2  = self.latitude
        long2 = self.longitude

        degree_to_rad = float (pi / 180.0)

        d_lat = (lat2 - lat1) * degree_to_rad
        d_long = (long2 - long1) * degree_to_rad

        a = pow (sin (d_lat / 2), 2) + cos (lat1 * degree_to_rad) * cos (lat2 * degree_to_rad) * pow (sin (d_long / 2),
                                                                                                      2)
        c = 2 * atan2 (sqrt (a), sqrt (1 - a))
        return 6367 * c


class JourneyManager (models.Manager):

    @staticmethod
    def get_coordinate_lt_gt_kwargs(city, s='origin'):
        d = 3
        return {
            f'{s}__longitude__gt': city.longitude - d, f'{s}__longitude__lt': city.longitude + d,
            f'{s}__latitude__gt' : city.latitude  - d, f'{s}__latitude__lt':  city.latitude  + d
        }
        

    def all_ordered(self, **kwargs):
        qs = self.get_queryset ()
        if ('origin' in kwargs):
            origin = City.objects.get (pk=kwargs['origin'])
            qs = qs.filter (**self.get_coordinate_lt_gt_kwargs (city=origin, s='origin'))
        if ('destination' in kwargs):
            destination = City.objects.get (pk=kwargs['destination'])
            qs = qs.filter (**self.get_coordinate_lt_gt_kwargs (city=destination, s='destination'))
        return qs


class Journey(BaseModel):
    name        = models.CharField(max_length=255, unique=False, null=True, blank=True)
    origin      = models.ForeignKey(City, on_delete=models.SET_NULL, null=True, blank=True, related_name='journey_origin')
    destination = models.ForeignKey(City, on_delete=models.SET_NULL, null=True, blank=True, related_name='journey_destination')
    objects     = JourneyManager()
    def __str__(self):
        return f'{str(self.name)}: from {str(self.origin)} to {str(self.destination)}'
    
    
class Shipment(BaseModel):
    journey  = models.ForeignKey(Journey, on_delete=models.SET_NULL, null=True, blank=True, related_name='shipment')


class User(BaseUserModel):
    journeys = models.ManyToManyField(Journey)
