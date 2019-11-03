from rest_framework.filters     import SearchFilter
from rest_framework.views       import APIView
from rest_framework.response    import Response
from rest_framework.generics    import ListAPIView, RetrieveAPIView, CreateAPIView
from core.serializers           import CitySerializer,  CityNamesSerializer, JourneySerializer
from core.models                import City, Journey


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


class JourneyListAPIView (ListAPIView):
    serializer_class = JourneySerializer
    
    def get_params(self):
        kwargs      = {}
        origin      = self.request.query_params.get('origin')
        destination = self.request.query_params.get('destination')
        if origin:      kwargs['origin']      = int(origin)
        if destination: kwargs['destination'] = int(destination)
        return kwargs  # self.request.query_params
    
    def get_queryset(self):
        return Journey.objects.all_ordered(**self.get_params())
    
    # def get_serializer_context(self):
    #     return {
    #         'request': self.request,
    #         'format' : self.format_kwarg,
    #         'view'   : self,
    #         **self.get_params (),
    #     }
