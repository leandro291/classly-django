from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import generics
from django.contrib.auth import get_user_model
from rest_framework.generics import get_object_or_404
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated

from cursos.models import Curso
from cursos.api.permissions import IsCourseTeacher, IsTeacher
from tareas.api.serializers import TareaCreateSerializer, TareaSerializer
from tareas.models import Tarea

@extend_schema(tags=['Workhome'])
@extend_schema_view(
    get=extend_schema(
        summary='Lista las tareas de un curso',
        description='Devuelve las tareas del curso indicado según el rol: '
                    'teacher (cursos que dicta) o student (cursos donde está inscrito).',
    ),
    post=extend_schema(
        summary='Registra una nueva tarea',
        description='Crea una tarea en el curso indicado. Solo el teacher propietario del curso.',
        request={'multipart/form-data': TareaCreateSerializer},
    ),
)
class TareaCreateListView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated, IsCourseTeacher, IsTeacher]
    serializer_class = TareaSerializer
    parser_classes = (MultiPartParser, FormParser)

    def get_queryset(self):
        course_pk = self.kwargs['course_pk']
        user = self.request.user

        if user.rol == get_user_model().Roles.TEACHER:
            return Tarea.objects.is_teacher(user).filter(course_id=course_pk)

        return Tarea.objects.is_student(user).filter(course_id=course_pk)

    def perform_create(self, serializer):
        course_pk = self.kwargs['course_pk']
        course = get_object_or_404(
            Curso,
            id=course_pk,
            teacher = self.request.user,
        )
        serializer.save(course=course)


