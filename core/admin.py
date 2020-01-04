from django.contrib import admin
from core.models    import City, Country, Journey, User  #  , Shipment_dep
from django.contrib.auth.admin import UserAdmin

# admin.site.register(User)
# admin.site.register(Shipment_dep)


class CityInline(admin.TabularInline):
    model = City
    
    
@admin.register(User)
class CUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
            (None, {'fields': ('reset_token', '_avatar', '_phone', 'latitude', 'longitude' )}),
    )
    list_display = ('__str__', 'username', 'email', 'successful_journeys', 'latitude', 'longitude')


@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'name', 'iso', 'pk')
    inlines = [CityInline,]


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'name', 'country', 'population', 'latitude', 'longitude', 'pk')
    search_fields = ('name',)
    
    
@admin.register(Journey)
class JourneyAdmin(admin.ModelAdmin):
    raw_id_fields = ('origin', 'destination')
    list_display = ('__str__', 'name', 'user', 'date', 'pk')
