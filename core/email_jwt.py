from calendar import timegm
from datetime import datetime

from .models import User
from django.contrib.auth import authenticate
from django.utils.translation import ugettext as _
from rest_framework import serializers
from rest_framework_jwt.serializers import JSONWebTokenSerializer
from rest_framework_jwt.settings import api_settings
from .utils import reset_user_password_by_email
from django.core.exceptions import ObjectDoesNotExist


jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER


def custom_jwt_payload_handler(user):
    """ Custom payload handler
    Token encrypts the dictionary returned by this function, and can be decoded by rest_framework_jwt.utils.jwt_decode_handler
    """
    return {
        'user_id': user.pk,
        'email': user.email,
        'is_superuser': user.is_superuser,
        'username': user.username,
        'exp': datetime.utcnow() + api_settings.JWT_EXPIRATION_DELTA,
        'orig_iat': timegm(
            datetime.utcnow().utctimetuple()
        )
    }

from rest_framework_jwt.compat import PasswordField


class CustomJWTSerializer(JSONWebTokenSerializer):
    username_field = 'email'
    
    def __init__(self, *args, **kwargs):
        super(CustomJWTSerializer, self).__init__(*args, **kwargs)
        self.fields['password'] = PasswordField(write_only=True, required=False)
        self.fields['reset'] = serializers.BooleanField(required=False, write_only=True)

    def validate(self, attrs):
        password = attrs.get("password", '.')
        user_obj = User.objects.filter(email=attrs.get("email")).first()  # .user
        if not user_obj:
            user_obj = User.objects.filter(username=attrs.get("email")).first()
        if user_obj is not None:
            if user_obj.reset_token is not None and user_obj.reset_token != '':
                if user_obj.reset_token == password:
                    user_obj.set_password(password)
                    user_obj.reset_token = None
                    user_obj.save()
            credentials = {
                'username': user_obj.username,
                'password': password
            }
            if all(credentials.values()):
                user = authenticate(**credentials)
                if user:
                    if not user.is_active:
                        msg = _('User account is disabled.')
                        raise serializers.ValidationError(msg)

                    payload = custom_jwt_payload_handler(user_obj)

                    return {
                        'token': jwt_encode_handler(payload),
                        'user': user,
                    }
                else:
                    if attrs.get('reset'):
                        reset_user_password_by_email(user_obj)
                        return {
                            'token': 'reset token sent to ' + user_obj.email,
                            'user': user_obj,
                        }
                    msg = _('Unable to log in with provided credentials.')
                    raise serializers.ValidationError(msg)

            else:
                msg = _('Must include "{username_field}" and "password".')
                msg = msg.format(username_field=self.username_field)
                raise serializers.ValidationError(msg)

        else:
            msg = _('Account with this email/username does not exists')
            raise serializers.ValidationError(msg)
