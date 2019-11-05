from django.contrib import admin
from core.models    import City, Country, Journey, User  #  , Shipment_dep

admin.site.register(User)
# admin.site.register(Shipment_dep)


class CityInline(admin.TabularInline):
    model = City
    

@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'name', 'iso', 'pk')
    inlines = [CityInline,]


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'name', 'population', 'latitude', 'longitude', 'pk')
    search_fields = ('name',)
    
    
@admin.register(Journey)
class JourneyAdmin(admin.ModelAdmin):
    raw_id_fields = ('origin', 'destination')
    list_display = ('__str__', 'name', 'pk')
