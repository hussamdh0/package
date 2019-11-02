from django.contrib.auth.models import AbstractUser
from django.db                  import models

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
        
        
class Place(models.Model):
    city        = models.CharField(max_length=255, unique=False, null=True, blank=True)
    latitude    = models.FloatField(unique=False, null=True, blank=True)
    longitude   = models.FloatField(unique=False, null=True, blank=True)


class Shipment(BaseModel):
    name        = models.CharField(max_length=255, unique=False, null=True, blank=True)
    origin      = models.ForeignKey(Place, on_delete=models.SET_NULL, null=True, blank=True, related_name='shipment_origin')
    destination = models.ForeignKey(Place, on_delete=models.SET_NULL, null=True, blank=True, related_name='shipment_destination')


class User(BaseUserModel):
    shipments   = models.ManyToManyField(Shipment)
