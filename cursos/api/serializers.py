from rest_framework import serializers
from cursos.models import Curso, Inscripcion
from django.contrib.auth import get_user_model

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ['id', 'first_name', 'last_name', 'email']

class CursoSerializer(serializers.ModelSerializer):
    teacher = UserSerializer(read_only=True)

    class Meta:
        model = Curso
        fields = ['id', 'name', 'description', 'period', 'teacher', 'registration_code',
                  'status', 'created_at', 'updated_at']

        read_only_fields = ['id', 'created_at', 'updated_at', 'registration_code',
                            'status']

class UnirseCursoSerializer(serializers.ModelSerializer):
    registration_code = serializers.CharField(write_only=True)

    class Meta:
        model = Inscripcion
        fields = ['id','registration_code', 'course', 'student', 'status', 'joined_at']
        read_only_fields = ['id', 'course', 'student', 'joined_at', 'status']

    def validate_registration_code(self, value):
        curso = Curso.objects.filter(
            registration_code=value,
            status=Curso.Status.ACTIVE
        ).first()

        if curso is None:
            raise serializers.ValidationError('Codigo invalido')

        if curso.teacher == self.context['request'].user:
            raise serializers.ValidationError('No puedes inscribirte a tu propio curso.')

        self.curso = curso
        return value

    def create(self, validated_data):
        inscripcion, creada = Inscripcion.objects.get_or_create(
            course=self.curso,
            student=self.context['request'].user,
            defaults={'status': Inscripcion.Status.ACTIVE}
        )

        if not creada:
            if inscripcion.status == Inscripcion.Status.DEACTIVATED:
                inscripcion.status = Inscripcion.Status.ACTIVE
                inscripcion.save()
            else:
                raise serializers.ValidationError('Ya estas inscrito en este curso.')

        return inscripcion