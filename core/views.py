from rest_framework.filters     import SearchFilter
from rest_framework.generics    import ListAPIView, RetrieveAPIView, CreateAPIView
from core.serializers import CitySerializer
from core.models import City


class CityListAPIView(ListAPIView):
    serializer_class = CitySerializer
    
    def get_queryset(self):
        kwargs = {}
        longitude = self.request.query_params.get('longitude')
        latitude  = self.request.query_params.get('latitude')
        if longitude: kwargs['longitude'] = float(longitude)
        if latitude:  kwargs['latitude']  = float(latitude)
        return City.objects.all_ordered(**kwargs)
