from django.urls import path
from cursos.api import views

urlpatterns = [
    path('course/', views.CursoListCreateView.as_view()),
    path('course/<int:pk>/', views.CursoRetrieveUpdateDestroyAPIView.as_view()),
]