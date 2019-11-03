from rest_framework             import serializers
from core.models                import City, Journey


class CitySerializer(serializers.ModelSerializer):
    country  = serializers.StringRelatedField()
    distance = serializers.SerializerMethodField()
    
    class Meta:
        model = City
        fields = ['id', 'name', 'country', 'population', 'longitude', 'latitude', 'distance',]  # '__all__'
        
    def get_distance(self, instance):
        if 'latitude' in self.context and 'longitude' in self.context and self.context['latitude'] and self.context['longitude']:
            return instance.distance(latitude=self.context['latitude'], longitude=self.context['longitude'], )
        return None
    
    
class CityNamesSerializer(CitySerializer):
    class Meta:
        model = City
        fields = ('name',)


class JourneySerializer (serializers.ModelSerializer):
    origin      = serializers.StringRelatedField()
    destination = serializers.StringRelatedField()
    
    class Meta:
        model = Journey
        fields = ['id', 'name', 'origin', 'destination',]
    