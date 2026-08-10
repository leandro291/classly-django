from django.urls import path
from cursos.api import views

urlpatterns = [
    path('course/', views.CursoListCreateView.as_view()),
    path('course/join/', views.UnirseCursoView.as_view()),
    path('course/<int:pk>/', views.CursoRetrieveUpdateDestroyView.as_view()),
]