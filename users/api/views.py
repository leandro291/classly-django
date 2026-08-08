from rest_framework import generics

from users.api.serializers import UserRegisterSerializer
from users.models import User

class UserRegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserRegisterSerializer
