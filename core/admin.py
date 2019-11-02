from django.contrib import admin
from core.models import Place, Shipment, User
# Register your models here.

admin.site.register(User)
admin.site.register(Place)
admin.site.register(Shipment)
