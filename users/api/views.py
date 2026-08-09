from rest_framework import generics
from rest_framework_simplejwt.views import TokenObtainPairView

from users.api.serializers import UserRegisterSerializer, UserLoginSerializer

class UserRegisterView(generics.CreateAPIView):
    serializer_class = UserRegisterSerializer

class UserLoginView(TokenObtainPairView):
    serializer_class = UserLoginSerializer

