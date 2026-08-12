from datetime import date

from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from tareas.models import Tarea, Entrega, ArchivoEntrega


@extend_schema_field(
    {
        'type': 'string',
        'format': 'binary'
    }
)
class TareaFileField(serializers.FileField):
    pass

class TareaCreateSerializer(serializers.ModelSerializer):
    file_upload = TareaFileField(write_only=True, required=False)

    class Meta:
        model = Tarea
        fields = ['title', 'description', 'file_upload', 'due_date', 'max_score']

class TareaSerializer(serializers.ModelSerializer):
    file_upload = TareaFileField(write_only=True, required=False)
    file = serializers.SerializerMethodField()

    class Meta:
        model = Tarea
        fields = ['id', 'course', 'title', 'description', 'file', 'file_upload', 'created_at', 'due_date', 'max_score']
        read_only_fields = ['id', 'course', 'created_at']

    def get_file(self, obj):
        return obj.file.url if obj.file else None

    def create(self, validated_data):
        archivo = validated_data.pop('file_upload', None)
        tarea = Tarea.objects.create(**validated_data)
        if archivo:
            tarea.file = archivo
            tarea.save(update_fields=['file'])
        return tarea

    def update(self, instance, validated_data):
        archivo = validated_data.pop('file_upload', None)
        instance = super().update(instance, validated_data)
        if archivo:
            instance.file = archivo
            instance.save(update_fields=['file'])
        return instance

    def validate_due_date(self, value):
        if value < date.today():
            raise serializers.ValidationError('La fecha límite no puede ser anterior a hoy.')
        return value


@extend_schema_field({
    "type": "array",
    "items": {
        "type": "string",
        "format": "binary"
    }
})
class MultipleImageField(serializers.ListField):
    child = serializers.FileField(allow_empty_file=False, use_url=False)

class ArchivoEntregaSerializer(serializers.ModelSerializer):
    file = serializers.SerializerMethodField()

    class Meta:
        model = ArchivoEntrega
        fields = ['id', 'file', 'created_at']

    def get_file(self, obj):
        return obj.file.url if obj.file else None

class EntregaCreateSerializer(serializers.ModelSerializer):
    file_upload = MultipleImageField(write_only=True, required=False)

    class Meta:
        model = Entrega
        fields = ['student_comment', 'file_upload']

class EntregaSerializer(serializers.ModelSerializer):
    archivos = ArchivoEntregaSerializer(read_only=True, many=True)
    file_upload = MultipleImageField(write_only=True, required=False)

    class Meta:
        model = Entrega
        fields = ['id', 'assignment', 'student', 'submitted_at', 'student_comment', 'teacher_comment',
                  'status', 'score', 'archivos', 'file_upload']
        read_only_fields = ['id', 'assignment', 'student', 'submitted_at', 'status', 'score', 'teacher_comment']

    def create(self, validated_data):
        file_upload = validated_data.pop('file_upload', [])
        entrega = Entrega.objects.create(**validated_data)

        for file in file_upload:
            ArchivoEntrega.objects.create(
                submission=entrega,
                file=file,
            )

        return entrega

    def update(self, instance, validated_data):
        file_upload = validated_data.pop('file_upload', None)
        entrega = super().update(instance, validated_data)

        if entrega and file_upload is not None:
            instance.archivos.all().delete()
            for file in file_upload:
                ArchivoEntrega.objects.create(
                    submission=entrega,
                    file=file,
                )

        return entrega

class CalificarEntregaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Entrega
        fields = ['score', 'teacher_comment']

    def validate_score(self, value):
        if value < 0 or value > 20:
            raise serializers.ValidationError(f"La calificación debe estar entre 0 y 20.")

        return value




