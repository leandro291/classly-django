from django.db import models
from cursos.models import Curso, Inscripcion
from cloudinary.models import CloudinaryField

class MaterialQuerySet(models.QuerySet):
    def is_teacher(self, user):
        return self.filter(course__teacher=user)

    def is_student(self, user):
        return self.filter(course__inscripciones__student=user,
                           course__inscripciones__status=Inscripcion.Status.ACTIVE
                           )
# Create your models here.
class Material(models.Model):

    objects = MaterialQuerySet.as_manager()

    course = models.ForeignKey(
        Curso,
        on_delete=models.CASCADE,
        related_name='materials',
    )

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'material'
        verbose_name = 'material'
        verbose_name_plural = 'materiales'
        ordering = ['created_at']

    def __str__(self):
        return self.title

class ArchivoMaterial(models.Model):

    material = models.ForeignKey(
        Material,
        on_delete=models.CASCADE,
        related_name='archivo_materials',
    )

    file = CloudinaryField('file', folder='materials')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'archivo_material'
        verbose_name = 'archivo_material'
        verbose_name_plural = 'archivo_materiales'

    def __str__(self):
        return f"Archivo creado para {self.material.title}"