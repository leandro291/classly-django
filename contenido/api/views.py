from requests import post
from rest_framework import generics
from rest_framework.generics import get_object_or_404
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated
from contenido.api.serializers import MaterialSerializer
from cursos.api.permissions import IsTeacher
from cursos.models import Curso

from drf_spectacular.utils import extend_schema, extend_schema_view

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
class CreateMaterialView(generics.CreateAPIView):
    permission_classes = [IsTeacher, IsAuthenticated]
    serializer_class = MaterialSerializer
    parser_classes = [MultiPartParser, FormParser]

    def perform_create(self, serializer):
        course_pk = self.kwargs['course_pk']
        course = get_object_or_404(
            Curso,
            id=course_pk,
            teacher=self.request.user,
        )
        serializer.save(course=course)
