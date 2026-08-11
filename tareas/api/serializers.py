from datetime import date

from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers
from tareas.models import Tarea

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





