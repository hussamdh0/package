from rest_framework             import serializers
from core.models import City


class CitySerializer(serializers.ModelSerializer):
    country  = serializers.StringRelatedField()
    distance = serializers.SerializerMethodField()
    
    class Meta:
        model = City
        fields = ['id', 'name', 'country', 'population', 'longitude', 'latitude', 'distance',]  # '__all__'
        
    def get_distance(self, instance):
        if self.context['latitude'] and self.context['longitude']:
            return instance.distance_squared(latitude=self.context['latitude'], longitude=self.context['longitude'], )
        return None
