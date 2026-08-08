from rest_framework import serializers
from cursos.models import Curso

class CursoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Curso
        fields = ['id', 'name', 'description', 'period', 'teacher', 'registration_code',
                  'status', 'created_at', 'updated_at']

        read_only_fields = ['id', 'created_at', 'updated_at', 'teacher', 'registration_code',
                            'status']