from django.contrib.auth.models import AbstractUser
from django.db                  import models
from core.managers              import CityManager

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
    def distance_squared(self, longitude, latitude):
        a = longitude - self.longitude
        b = latitude  - self.latitude
        return a**2 + b**2
    
class Shipment(BaseModel):
    name        = models.CharField(max_length=255, unique=False, null=True, blank=True)
    origin      = models.ForeignKey(City, on_delete=models.SET_NULL, null=True, blank=True, related_name='shipment_origin')
    destination = models.ForeignKey(City, on_delete=models.SET_NULL, null=True, blank=True, related_name='shipment_destination')
    
    def __str__(self):
        return f'{str(self.name)}: from {str(self.origin)} to {str(self.destination)}'

class User(BaseUserModel):
    shipments   = models.ManyToManyField(Shipment)
