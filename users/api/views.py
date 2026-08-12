from rest_framework import generics
from drf_spectacular.utils import extend_schema
from users.api.serializers import UserRegisterSerializer, UserLoginSerializer
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

@extend_schema(
    tags=['Auth'],
    summary='Registra un nuevo usuario',
    description='Crea un usuario autenticable. Sin autenticación requerida.',
)
class UserRegisterView(generics.CreateAPIView):
    serializer_class = UserRegisterSerializer

@extend_schema(
    tags=['Auth'],
    summary='Inicia sesión',
    description='Autentica con email y contraseña y devuelve los tokens access y refresh.',
)
class UserLoginView(TokenObtainPairView):
    serializer_class = UserLoginSerializer


@extend_schema(
    tags=['Auth'],
    summary='Renueva el access token',
    description='Usa el refresh token para obtener un nuevo access token.',
)
class UserRefreshView(TokenRefreshView):
    pass

