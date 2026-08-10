from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model

from cursos.api.permissions import IsTeacher, IsCourseTeacher, IsStudent
from cursos.api.serializers import CursoSerializer, UnirseCursoSerializer
from cursos.models import Curso

@extend_schema(tags=['Course'])
@extend_schema_view(
    get=extend_schema(
        summary='Lista todos los cursos',
        description='Obtiene una lista de cursos según el rol del usuario. Solo usuarios autenticados.',
    ),
    post=extend_schema(
        summary='Registra un nuevo curso',
        description='Crea un nuevo curso. Solo usuarios autenticados con rol de teacher.',
    ),
)

class CursoListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated, IsTeacher]
    serializer_class = CursoSerializer

    def get_queryset(self):
        usuario = self.request.user
        if usuario.rol == get_user_model().Roles.TEACHER:
            return Curso.objects.is_teacher(usuario)

        return Curso.objects.is_student(usuario)

    def perform_create(self, serializer):
        serializer.save(teacher=self.request.user)

@extend_schema(tags=['Course'])
@extend_schema_view(
    get=extend_schema(
        summary='Obtiene un curso por su ID',
        description='Obtiene los detalles de un curso por su ID. Solo usuarios autenticados '
                    'que pertenezcan al curso.',
    ),
    put=extend_schema(
        summary='Actualiza un curso por su ID',
        description='Reemplaza todos los campos del curso. Solo el teacher propietario.',
    ),
    patch=extend_schema(
        summary='Actualiza parcialmente un curso',
        description='Actualiza solo los campos enviados. Solo el teacher propietario.',
    ),
    delete=extend_schema(
        summary='Elimina un curso',
        description='Borra el curso. Solo el teacher propietario.',
    ),
)
class CursoRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated, IsCourseTeacher]
    serializer_class = CursoSerializer

    def get_queryset(self):
        if self.request.user.rol == get_user_model().Roles.TEACHER:
            return Curso.objects.is_teacher(self.request.user)

        return Curso.objects.is_student(self.request.user)

@extend_schema(tags=['Course'])
@extend_schema_view(
    post=extend_schema(
        summary='Inscribe al estudiante en un curso',
        description='Valida el código de registro y crea la inscripción. Solo rol student.',
    ),
)
class UnirseCursoView(generics.CreateAPIView):
    serializer_class = UnirseCursoSerializer
    permission_classes = [IsAuthenticated, IsStudent]