from django.urls import path

from .views import add_city_data

app_name = "template_scripts"

urlpatterns = [
    path('add_city_data/', add_city_data, name="add_city_data"),
]
