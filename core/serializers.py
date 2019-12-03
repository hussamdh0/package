from rest_framework             import serializers
from core.models                import City, Journey, User


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
        fields = ('id', 'name',)


class JourneySerializer(serializers.ModelSerializer):
    origin      = serializers.JSONField(required=False, source='_origin')
    destination = serializers.JSONField(required=False, source='_destination')
    phone       = serializers.JSONField(required=False)
    email       = serializers.JSONField(required=False)
    
    class Meta:
        model = Journey
        fields = ['id', 'name', 'date', 'origin', 'destination', 'phone', 'email',]
    
    def create(self, validated_data):
        journey = Journey.objects.create(**validated_data, user=self.context['request'].user)
        return journey
    

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model  = User
        fields = ['id', 'username', 'password',]
        extra_kwargs = { 'password': {'write_only': True}, }
    
    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user