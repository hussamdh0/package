from django.urls import path
from rest_framework_jwt.views import obtain_jwt_token
from core.views import CityListAPIView, JourneyListAPIView

app_name = "core"

urlpatterns = [
    path('login', obtain_jwt_token, name='login'),
    path('city',    CityListAPIView.as_view(),     name='city'),
    path('journey', JourneyListAPIView.as_view(),  name='journey'),

]
