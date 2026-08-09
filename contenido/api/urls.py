from django.urls import path
from contenido.api import views

urlpatterns = [
    path('course/<int:course_pk>/material/', views.CreateMaterialView.as_view()),
]