from django.urls import path
from tareas.api import views

urlpatterns = [
    path('course/<int:course_pk>/tarea/', views.TareaCreateListView.as_view()),
    path('tarea/<int:pk>/', views.TareaRetrieveUpdateDestroyAPIView.as_view()),
    path('tarea/<int:workhome_pk>/entrega/', views.EntregaCreateListView.as_view()),
    path('entrega/<int:pk>/', views.EntregaRetrieveUpdateDestroyAPIView.as_view()),
]