from django.urls import path

from core.views import CityListAPIView

app_name = "core"

urlpatterns = [

    path('city', CityListAPIView.as_view(), name='city'),

]
