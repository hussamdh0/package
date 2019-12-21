from django.urls                import path
from rest_framework_jwt.views   import obtain_jwt_token
from .email_jwt                 import CustomJWTSerializer
from rest_framework_jwt.views   import ObtainJSONWebToken

from core.views                 import (
    CityLV,
    JourneyLCV,
    UserCV,
    UserRUV,
    # CreateJourneyAPIView,
    JourneyRUDV,
    index,
)
app_name = "core"

urlpatterns = [
    path('',                    index,                              name='index'),
    
    # path('login',               obtain_jwt_token,                   name='login'),
    
    path('login',
         ObtainJSONWebToken.as_view(serializer_class=CustomJWTSerializer),
         name='login'),
    
    path('add_user', UserCV.as_view(), name='add_user'),
    
    path('city', CityLV.as_view(), name='city'),
    
    path('user', UserRUV.as_view(), name='user'),
    
    # path('add_journey',         CreateJourneyAPIView.as_view(),     name='add_journey'),
    
    path('journey', JourneyLCV.as_view(), name='journey'),
    
    path('journey/<int:id>', JourneyRUDV.as_view(), name='journey_rud'),
]
