from django.urls import path
from users.api import views
from rest_framework_simplejwt.views import (
    TokenRefreshView,
)

urlpatterns = [
    path('auth/register/', views.UserRegisterView.as_view(), name='user_register'),
    path('auth/login/', views.UserLoginView.as_view(), name='token_obtain_pair'),
]