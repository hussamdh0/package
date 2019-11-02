from django.contrib import admin
from core.models import City, Country, Shipment, User
# Register your models here.

admin.site.register(User)
admin.site.register(Shipment)


class CityInline(admin.TabularInline):
    model = City


@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'name', 'iso', 'pk')
    inlines = [
        CityInline,
    ]


@admin.register (City)
class CityAdmin (admin.ModelAdmin):
    list_display = ('__str__', 'name', 'population', 'latitude', 'longitude', 'pk')
