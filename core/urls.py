from django.urls import path

from core.views import CityListAPIView, JourneyListAPIView

app_name = "core"

urlpatterns = [

    path('city',    CityListAPIView.as_view(),     name='city'),
    path('journey', JourneyListAPIView.as_view(),  name='journey'),

]
