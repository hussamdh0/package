from rest_framework.filters     import SearchFilter
from rest_framework.views       import APIView
from rest_framework.response    import Response
from rest_framework.generics    import ListAPIView, RetrieveAPIView, CreateAPIView
from core.serializers           import (
    CitySerializer,
    CityNamesSerializer,
    JourneySerializer,
    UserSerializer,
)
from core.models                import City, Journey, User
from datetime                   import date, timedelta, datetime


class CityListAPIView(ListAPIView):
    serializer_class = CitySerializer

    def get_params(self):
        kwargs = {}
        longitude = self.request.query_params.get('longitude')
        latitude  = self.request.query_params.get('latitude')
        if longitude: kwargs['longitude'] = float(longitude)
        if latitude:  kwargs['latitude']  = float(latitude)
        
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


class JourneyListAPIView(ListAPIView):
    serializer_class = JourneySerializer
    
    def get_params(self):
        kwargs          = {}
        _date           = self.request.query_params.get('date')
        date_tolerance  = self.request.query_params.get('date_tolerance')
        origin          = self.request.query_params.get('origin')
        destination     = self.request.query_params.get('destination')
        radius          = self.request.query_params.get('radius')
        if _date:
            kwargs['date']              = datetime.strptime(_date, '%Y-%m-%d').date()
            kwargs['date_tolerance']    = 1
        if date_tolerance:  kwargs['date_tolerance']    = int(date_tolerance)
        if origin:          kwargs['origin']            = int(origin)
        if destination:     kwargs['destination']       = int(destination)
        if radius:          kwargs['radius']            = float(radius)
        return kwargs  #     self.request.query_params
    
    def get_queryset(self):
        return Journey.objects.all_ordered(**self.get_params())


class CreateUserAPIView(APIView):
    def post(self, request):
        serialized = UserSerializer(data=request.data)
        if serialized.is_valid():
            # User.objects.create_user(
            serialized.save()
            # )
            return Response(serialized.data)
        else:
            return Response(serialized._errors)
