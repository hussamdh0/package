from django.contrib import admin
from django import forms
from core.models import City, Country, Shipment, User
# Register your models here.

admin.site.register(User)
# admin.site.register(Shipment)


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
    search_fields = ('name',)
    
@admin.register(Shipment)
class ShipmentAdmin(admin.ModelAdmin):
    # list_filter = ('origin__name',)
    raw_id_fields = ('origin', 'destination')
    # fields = ['fk_contract']
    list_display = ('__str__', 'name', 'pk')






# class ShipmentForm(forms.ModelForm):
#
#     class Meta:
#         model = Shipment
#         fields = ['origin']
#
#     def __init__(self, *args, **kwargs):
#         super(ShipmentForm, self).__init__(*args, **kwargs)
#         self.fields['origin'].queryset = City.objects.filter(name='Cairo')  # self.rigin)
#
#
#
# @admin.register(Shipment)
# class ShipmentAdmin(admin.ModelAdmin):
#     fieldsets = [
#         ('Origin',        {'fields': ['filter', 'origin']}),
#         #('Tralala',        {'fields': ['tralala']}),
#     ]
#     list_display = ('__str__', 'name', 'origin', 'pk')
#     search_fields = ['origin__name',]
#     form = ShipmentForm