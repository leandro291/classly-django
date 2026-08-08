from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model

from cursos.api.permissions import IsTeacher, IsCourseTeacher
from cursos.api.serializers import CursoSerializer
from cursos.models import Curso

class CursoListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated, IsTeacher]
    serializer_class = CursoSerializer

    def get_queryset(self):
        if self.request.user.rol == get_user_model().Roles.TEACHER:
            return Curso.objects.is_teacher(self.request.user)

        return Curso.objects.is_student(self.request.user)

    def perform_create(self, serializer):
        serializer.save(teacher=self.request.user)

class CursoRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated, IsCourseTeacher]

    serializer_class = CursoSerializer

    def get_queryset(self):
        if self.request.user.rol == get_user_model().Roles.TEACHER:
            return Curso.objects.is_teacher(self.request.user)

        return Curso.objects.is_student(self.request.user)