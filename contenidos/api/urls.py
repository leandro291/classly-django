from django.urls import path
from contenidos.api import views

urlpatterns = [
    path('course/<int:course_pk>/material/', views.MaterialListCreateView.as_view()),
    path('material/<int:pk>/', views.MaterialRetrieveUpdateDestroyView.as_view())
]