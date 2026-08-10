from rest_framework import generics
from rest_framework.generics import get_object_or_404
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated

from contenidos.api.permissions import IsMaterialTeacher
from contenidos.api.serializers import MaterialSerializer
from contenidos.models import Material
from cursos.api.permissions import IsTeacher
from cursos.models import Curso, Inscripcion

from drf_spectacular.utils import extend_schema

@extend_schema(
    tags=['Course'],
    request={
        'multipart/form-data': {
            'type': 'object',
            'properties': {
                'title': {'type': 'string'},
                'description': {'type': 'string'},
                'archivos': {
                    'type': 'array',
                    'items': {'type': 'string', 'format': 'binary'}
                }
            }
        }
    }
)
class MaterialListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = MaterialSerializer
    parser_classes = [MultiPartParser, FormParser]

    def get_queryset(self):
        course_pk = self.kwargs['course_pk']
        usuario = self.request.user

        if usuario.rol == 'teacher':
            try:
                curso = Curso.objects.get(id=course_pk, teacher=usuario)
            except Curso.DoesNotExist:
                curso = None
        else:
            try:
                curso = Inscripcion.objects.get(
                    course=course_pk,
                    student=usuario,
                ).course
            except Inscripcion.DoesNotExist:
                curso = None

        if curso is None:
            return Material.objects.none()

        return Material.objects.filter(course=curso)

    def perform_create(self, serializer):
        course_pk = self.kwargs['course_pk']
        course = get_object_or_404(
            Curso,
            id=course_pk,
            teacher=self.request.user,
        )
        serializer.save(course=course)

@extend_schema(
    methods=['PUT', 'PATCH'],
    tags=['material'],
    request={
        'multipart/form-data': {
            'type': 'object',
            'properties': {
                'title': {'type': 'string'},
                'description': {'type': 'string'},
                'archivos': {
                    'type': 'array',
                    'items': {'type': 'string', 'format': 'binary'}
                }
            }
        }
    }
)
class MaterialRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = MaterialSerializer
    permission_classes = [IsAuthenticated, IsMaterialTeacher, IsTeacher]
    parser_classes = [MultiPartParser, FormParser]

    def get_queryset(self):
        user = self.request.user

        if user.rol == 'teacher':
            return Material.objects.is_teacher(user)

        return Material.objects.is_student(user)


