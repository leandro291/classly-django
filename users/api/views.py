from rest_framework import generics
from rest_framework_simplejwt.views import TokenObtainPairView

from users.api.serializers import UserRegisterSerializer, UserLoginSerializer
from users.models import User

class UserRegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserRegisterSerializer

class UserLoginView(TokenObtainPairView):
    serializer_class = UserLoginSerializer

