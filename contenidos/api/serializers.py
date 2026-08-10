from rest_framework import serializers
from contenidos.models import Material, ArchivoMaterial
from drf_spectacular.utils import extend_schema_field

@extend_schema_field({
    "type": "array",
    "items": {
        "type": "string",
        "format": "binary"
    }
})
class MultipleImageField(serializers.ListField):
    child = serializers.FileField(allow_empty_file=False, use_url=False)

class MaterialArchivoSerializer(serializers.ModelSerializer):
    file = serializers.SerializerMethodField()

    class Meta:
        model = ArchivoMaterial
        fields = ['id', 'file']

    def get_file(self, obj):
        return obj.file.url if obj.file else None

class MaterialSerializer(serializers.ModelSerializer):
    archivos = MultipleImageField(write_only=True, required=False)
    archivo_materials = MaterialArchivoSerializer(many=True, read_only=True)

    class Meta:
        model = Material
        fields = ['id', 'course', 'title', 'description', 'created_at', 'archivos', 'archivo_materials']
        read_only_fields = ['id', 'course', 'created_at']

    def create(self, validated_data):
        archivos = validated_data.pop('archivos', [])
        material = Material.objects.create(**validated_data)

        for archivo in archivos:
            ArchivoMaterial.objects.create(
                material=material,
                file=archivo
            )

        return material

    def update(self, instance, validated_data):
        archivos = validated_data.pop('archivos', [])
        instance = super().update(instance, validated_data)

        if archivos:
            instance.archivo_materials.all().delete()
            for archivo in archivos:
                ArchivoMaterial.objects.create(
                    material=instance,
                    file=archivo
                )

        return instance