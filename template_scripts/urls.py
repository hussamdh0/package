from django.urls import path

from .views import add_city_data, add_journeys

app_name = "template_scripts"

urlpatterns = [
    path('city/',      add_city_data,  name="add_city_data"),
    path('journey/',   add_journeys,   name="add_journey_data"),
]
