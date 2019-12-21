#  from rest_framework.filters     import SearchFilter
from rest_framework.views       import APIView
from rest_framework.response    import Response
from rest_framework.generics    import ListAPIView, ListCreateAPIView, RetrieveUpdateDestroyAPIView, RetrieveUpdateAPIView
from core.serializers           import (
    CitySerializer,
    CityNamesSerializer,
    JourneySerializer,
    UserSerializer,
)
from core.models                import City, Journey, User
from datetime                   import date, timedelta, datetime
from django.shortcuts           import render
from .permissions               import IsObjectOwner
from django.http                import Http404
from rest_framework.exceptions  import NotAuthenticated


def index(request):
    return render(request, 'api_doc.html')


class CityLV(ListAPIView):
    serializer_class = CitySerializer

    def get_params(self):
        kwargs = {}
        longitude   = self.request.query_params.get('longitude')
        latitude    = self.request.query_params.get('latitude')
        if longitude:    kwargs['longitude'] = float(longitude)
        if latitude:     kwargs['latitude']  = float(latitude)
        
        if self.request.query_params.get('names_only'):
            # self.serializer_class._declared_fields = {}
            # self.serializer_class.Meta.fields = ['name',]
            self.serializer_class = CityNamesSerializer
            
        return kwargs

    def get_queryset(self):
        return City.objects.all_ordered(**self.get_params())

    def get_serializer_context(self):
        return {
            'request': self.request,
            'format': self.format_kwarg,
            'view': self,
            **self.get_params(),
        }


# class CityRetrieveUpdateDestroyAPIView(ListAPIView):
#     serializer_class = CitySerializer
#     lookup_field = 'id'
    
    
class JourneyLCV(ListCreateAPIView):
    serializer_class = JourneySerializer
    
    def get_params(self):
        kwargs          = {}
        _date           = self.request.query_params.get('date')
        date_tolerance  = self.request.query_params.get('date_tolerance')
        origin          = self.request.query_params.get('origin')
        destination     = self.request.query_params.get('destination')
        radius          = self.request.query_params.get('radius')
        my_journeys     = self.request.query_params.get('my_journeys')
        if _date:
            kwargs['date']              = datetime.strptime(_date, '%Y-%m-%d').date()
            kwargs['date_tolerance']    = 1
        if date_tolerance:  kwargs['date_tolerance']    = int(date_tolerance)
        if origin:          kwargs['origin']            = origin
        if destination:     kwargs['destination']       = destination
        if radius:          kwargs['radius']            = float(radius)
        if my_journeys and self.request.user and not self.request.user.is_anonymous:
                            kwargs['user']              = self.request.user

        return kwargs  #     self.request.query_params
    
    def get_queryset(self):
        return Journey.objects.all_ordered(**self.get_params())


class JourneyRUDV(RetrieveUpdateDestroyAPIView):
    queryset = Journey.objects.all()
    serializer_class = JourneySerializer
    permission_classes = [IsObjectOwner,]
    lookup_field = 'id'
    

class UserRUV(RetrieveUpdateAPIView):
    serializer_class = UserSerializer

    def get_object(self):
        if self.request.user.is_authenticated:
            return self.request.user
        raise Http404
    

class UserCV(APIView):
    def post(self, request):
        serialized = UserSerializer(data=request.data)
        if serialized.is_valid():
            serialized.save()
            return Response(serialized.data)
        else:
            return Response(serialized._errors, status=400)
