from rest_framework.filters     import SearchFilter
from rest_framework.generics    import ListAPIView, RetrieveAPIView, CreateAPIView
from core.serializers import CitySerializer
from core.models import City


class CityListAPIView(ListAPIView):
    serializer_class = CitySerializer
    
    def get_kwargs(self):
        kwargs = {}
        longitude = self.request.query_params.get('longitude')
        latitude  = self.request.query_params.get('latitude')
        if longitude: kwargs['longitude'] = float(longitude)
        if latitude:  kwargs['latitude']  = float(latitude)
        return kwargs
    
    def get_queryset(self):
        return City.objects.all_ordered(**self.get_kwargs())

    def get_serializer_context(self):
        return {
            'request': self.request,
            'format': self.format_kwarg,
            'view': self,
            **self.get_kwargs(),
        }
