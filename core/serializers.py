from rest_framework              import serializers
from core.models                 import City, Journey, User

from rest_framework_jwt.settings import api_settings
jwt_encode_handler  = api_settings.JWT_ENCODE_HANDLER
jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER


class UserSerializer(serializers.ModelSerializer):
    token = serializers.CharField(read_only=True)
    full_name = serializers.CharField(required=False)
    avatar = serializers.CharField(required=False, allow_blank=True)
    
    class Meta:
        model = User
        fields = ['id', 'username', 'password', 'email', 'token',
                  'address',
                  'successful_journeys', 'avatar', 'full_name',
                  'longitude', 'latitude', ]
        extra_kwargs = {'password'           : {'write_only': True},
                        'username'           : {'required':   False},
                        'address'            : {'required':   False},
                        'successful_journeys': {'read_only':  True},
                        # 'email':    {'write_only': True},
                        }
    
    def create(self, validated_data):
        if 'username' not in validated_data:
            validated_data['username'] = validated_data['email']
        user    = User.objects.create_user(**validated_data)
        payload = jwt_payload_handler(user)
        token   = jwt_encode_handler(payload)
        return {
            'id'      : user.id,
            'username': user.username,
            'email'   : user.email,
            'token'   : token
        }
    
    def update(self, instance, validated_data):
        for k, v in validated_data.items():
            setattr(instance, k, v)
        instance.save()
        return instance


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


class JourneySerializer(serializers.ModelSerializer):
    origin      = serializers.JSONField(required=False, source='_origin')
    destination = serializers.JSONField(required=False, source='_destination')
    phone       = serializers.JSONField(required=False)
    email       = serializers.JSONField(required=False)
    # date        = serializers.JSONField(required=False, source='_date')
    user        = UserSerializer(read_only=True)
    
    class Meta:
        model = Journey
        fields = ['id', 'name',  'origin', 'destination',
                  'date', 'time',
                  'phone', 'email',
                  'description', 'available_weight',
                  'successful',
                  'user']
    
    def create(self, validated_data):
        journey = Journey.objects.create(**validated_data, user=self.context['request'].user)
        return journey
