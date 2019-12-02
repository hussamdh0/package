from django.urls                import path
from rest_framework_jwt.views   import obtain_jwt_token
from core.views                 import (
    CityListAPIView,
    JourneyListAPIView,
    CreateUserAPIView,
    CreateJourneyAPIView,
    JourneyRUDAPIView,
    index,
)
app_name = "core"

urlpatterns = [
    path('',                    index,                              name='index'),
    
    path('login',               obtain_jwt_token,                   name='login'),
    path('add_user',            CreateUserAPIView.as_view(),        name='add_user'),
    
    path('city',                CityListAPIView.as_view(),          name='city'),
    
    path('add_journey',         CreateJourneyAPIView.as_view(),     name='add_journey'),
    path('journey',             JourneyListAPIView.as_view(),       name='journey'),
    path('journey/<int:id>',    JourneyRUDAPIView.as_view(),        name='journey_rud'),
]
