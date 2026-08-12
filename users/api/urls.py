from django.urls import path
from users.api import views

urlpatterns = [
    path('auth/register/', views.UserRegisterView.as_view(), name='user_register'),
    path('auth/login/', views.UserLoginView.as_view(), name='token_obtain_pair'),
    path('auth/refresh/', views.UserRefreshView.as_view(), name='token_refresh'),
]