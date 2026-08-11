from django.contrib.auth import get_user_model
from rest_framework import generics
from rest_framework.generics import get_object_or_404
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated

from contenidos.api.permissions import IsMaterialTeacher
from contenidos.api.serializers import MaterialCreateSerializer, MaterialSerializer
from contenidos.models import Material
from cursos.api.permissions import IsTeacher
from cursos.models import Curso

from drf_spectacular.utils import extend_schema, extend_schema_view

@extend_schema(tags=['Material'])
@extend_schema_view(
    get=extend_schema(
        summary='Lista los materiales de un curso',
        description='Devuelve los materiales del curso indicado según el rol: '
                    'teacher (cursos que dicta) o student (cursos donde está inscrito).',
    ),
    post=extend_schema(
        summary='Registra un material con sus archivos',
        description='Crea un material y sus archivos. Solo el teacher propietario del curso.',
        request={'multipart/form-data': MaterialCreateSerializer},
    ),
)
class MaterialListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated, IsTeacher]
    serializer_class = MaterialSerializer
    parser_classes = [MultiPartParser, FormParser]

    def get_queryset(self):
        course_pk = self.kwargs['course_pk']
        user = self.request.user

        if user.rol == get_user_model().Roles.TEACHER:
            return Material.objects.is_teacher(user).filter(course_id=course_pk)

        return Material.objects.is_student(user).filter(course_id=course_pk)

    def perform_create(self, serializer):
        course = get_object_or_404(
            Curso,
            id=self.kwargs['course_pk'],
            teacher=self.request.user,
        )
        serializer.save(course=course)

@extend_schema(tags=['Material'])
@extend_schema_view(
    get=extend_schema(
        summary='Obtiene un material por su ID',
        description='Detalle de un material. Accesible para el teacher propietario del curso '
                    'o los estudiantes inscritos en él.',
    ),
    put=extend_schema(
        summary='Actualiza un material',
        description='Reemplaza un material y sus archivos. Solo el teacher propietario del curso.',
        request={'multipart/form-data': MaterialCreateSerializer},
    ),
    patch=extend_schema(
        summary='Actualiza parcialmente un material',
        description='Actualiza campos específicos de un material. Solo el teacher propietario del curso.',
        request={'multipart/form-data': MaterialCreateSerializer},
    ),
    delete=extend_schema(
        summary='Elimina un material',
        description='Borra un material y sus archivos. Solo el teacher propietario del curso.',
    ),
)
class MaterialRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = MaterialSerializer
    permission_classes = [IsAuthenticated, IsMaterialTeacher, IsTeacher]
    parser_classes = [MultiPartParser, FormParser]

    def get_queryset(self):
        user = self.request.user

        if user.rol == get_user_model().Roles.TEACHER:
            return Material.objects.is_teacher(user)

        return Material.objects.is_student(user)
