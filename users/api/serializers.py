from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

class UserRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'telephone', 'rol',
                  'password', 'date_joined', 'updated_at']

        read_only_fields = ['id', 'date_joined', 'updated_at']

        extra_kwargs = {
            'password': {
                'write_only': True
            }
        }

    def create(self, validated_data):

        password = validated_data.pop('password')
        user = get_user_model().objects.create_user(
            password=password,
            **validated_data
        )

        return user

class UserLoginSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        token['username'] = user.username
        token['email'] = user.email
        token['rol'] = user.rol

        return token
