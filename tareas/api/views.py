from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import generics
from django.contrib.auth import get_user_model
from rest_framework.generics import get_object_or_404
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated

from cursos.models import Curso
from cursos.api.permissions import IsTeacher, IsStudent
from tareas.api.permissions import IsTareaTeacher, IsSubmitOwner
from tareas.api.serializers import TareaCreateSerializer, TareaSerializer, EntregaSerializer, EntregaCreateSerializer, \
    CalificarEntregaSerializer
from tareas.models import Tarea, Entrega


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
    permission_classes = [IsAuthenticated, IsTeacher]
    serializer_class = TareaSerializer
    parser_classes = [MultiPartParser, FormParser]

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

@extend_schema(tags=['Workhome'])
@extend_schema_view(
    get=extend_schema(
        summary='Obtiene una tarea por su ID',
        description='Detalle de una tarea. Accesible para el teacher propietario del curso '
                    'o los estudiantes inscritos en él.',
    ),
    put=extend_schema(
        summary='Actualiza una tarea',
        description='Reemplaza una tarea y su archivo. Solo el teacher propietario del curso.',
        request={'multipart/form-data': TareaCreateSerializer},
    ),
    patch=extend_schema(
        summary='Actualiza parcialmente una tarea',
        description='Actualiza campos específicos de una tarea. Solo el teacher propietario del curso.',
        request={'multipart/form-data': TareaCreateSerializer},
    ),
    delete=extend_schema(
        summary='Elimina una tarea',
        description='Borra una tarea. Solo el teacher propietario del curso.',
    ),
)
class TareaRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated, IsTareaTeacher, IsTeacher]
    serializer_class = TareaSerializer
    parser_classes = [MultiPartParser, FormParser]

    def get_queryset(self):
        user = self.request.user

        if user.rol == get_user_model().Roles.TEACHER:
            return Tarea.objects.is_teacher(user)

        return Tarea.objects.is_student(user)


@extend_schema(tags=['Submission'])
@extend_schema_view(
    get=extend_schema(
        summary='Lista las entregas de una tarea',
        description='Entregas de la tarea. Teacher: todas. Student: solo las suyas.',
    ),
    post=extend_schema(
        summary='Envía una entrega',
        description='El estudiante envía su entrega (comentario y archivos).',
        request={'multipart/form-data': EntregaCreateSerializer},
    ),
)
class EntregaCreateListView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated, IsStudent]
    serializer_class = EntregaSerializer
    parser_classes = [MultiPartParser, FormParser]

    def get_queryset(self):
        tarea_pk = self.kwargs['workhome_pk']
        user = self.request.user
        if user.rol == get_user_model().Roles.TEACHER:
            return Entrega.objects.is_teacher(user).filter(assignment_id=tarea_pk)

        return Entrega.objects.filter(assignment_id=tarea_pk, student=user)

    def perform_create(self, serializer):
        user = self.request.user
        workhome_pk = self.kwargs['workhome_pk']

        workhome = get_object_or_404(
            Tarea,
            id=workhome_pk,
        )

        serializer.save(
            student=user,
            assignment=workhome
        )

@extend_schema(tags=['Submission'])
@extend_schema_view(
    get=extend_schema(
        summary='Obtiene una entrega por su ID',
        description='Detalle de una entrega. Teacher: cualquier entrega de sus cursos. '
                    'Student: solo las suyas.',
        responses=EntregaSerializer,
    ),
    put=extend_schema(
        summary='Actualiza una entrega',
        description='Teacher: califica con puntaje y comentario. Student (dueño de la entrega): '
                    'edita su comentario y archivos.',
        request=CalificarEntregaSerializer,
        responses=EntregaSerializer,
    ),
    patch=extend_schema(
        summary='Actualiza parcialmente una entrega',
        description='Teacher: actualiza puntaje y/o comentario. Student (dueño): edita su '
                    'comentario y archivos.',
        request=CalificarEntregaSerializer,
        responses=EntregaSerializer,
    ),
    delete=extend_schema(
        summary='Elimina una entrega',
        description='El estudiante dueño puede borrar su entrega; el teacher puede borrar '
                    'cualquier entrega de sus cursos.',
    ),
)
class EntregaRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated, IsSubmitOwner]

    def get_serializer_class(self):
        user = self.request.user

        if user.rol == get_user_model().Roles.TEACHER:
            if self.request.method in ['PUT', 'PATCH']:
                return CalificarEntregaSerializer

            return EntregaSerializer

        return EntregaSerializer


    def get_queryset(self):
        user = self.request.user
        if user.rol == get_user_model().Roles.TEACHER:
            return Entrega.objects.is_teacher(user)

        return Entrega.objects.filter(student=user)



