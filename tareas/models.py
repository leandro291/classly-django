from cloudinary.models import CloudinaryField
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.conf import settings
from cursos.models import Curso

class TareaQuerySet(models.QuerySet):

    def is_teacher(self, user):
        return self.filter(course__teacher=user)

    def is_student(self, user):
        return self.filter(course__inscripciones__student=user)

class Tarea(models.Model):

    objects = TareaQuerySet.as_manager()

    course = models.ForeignKey(
        Curso,
        on_delete=models.CASCADE,
        related_name='tareas',
    )
    title = models.CharField(max_length=255)
    description = models.TextField()
    file = CloudinaryField('file', folder='tareas', blank=True, null=True)
    max_score = models.IntegerField(
        validators=[
            MinValueValidator(0),
            MaxValueValidator(20)
        ],
    )
    created_at = models.DateTimeField(auto_now_add=True)
    due_date = models.DateField()


    class Meta:
        db_table = 'tarea'
        verbose_name = 'tarea'
        verbose_name_plural = 'tareas'
        ordering = ['created_at']

    def __str__(self):
        return self.title

class Entrega(models.Model):
    class Status(models.TextChoices):
        A_TIEMPO = 'a_tiempo', 'A tiempo'
        TARDIA = 'tardia', 'Tardía'

    assignment = models.ForeignKey(
        Tarea,
        on_delete=models.CASCADE,
        related_name='entregas',
    )
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='entregas',
    )
    submitted_at = models.DateTimeField(auto_now_add=True)
    student_comment = models.TextField(blank=True)
    teacher_comment = models.TextField(blank=True)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.A_TIEMPO,
    )
    score = models.IntegerField(null=True, blank=True)

    class Meta:
        db_table = 'entrega'
        verbose_name = 'entrega'
        verbose_name_plural = 'entregas'
        ordering = ['submitted_at']
        constraints = [
            models.UniqueConstraint(
                fields=['assignment', 'student'],
                name='unique_entrega_tarea_estudiante'
            )
        ]

    def __str__(self):
        return f"Entrega de {self.student.username} para {self.assignment.title}"

class ArchivoEntrega(models.Model):
    submission = models.ForeignKey(
        Entrega,
        on_delete=models.CASCADE,
        related_name='archivos',
    )
    file = CloudinaryField('file', folder='entregas')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'archivo_entrega'
        verbose_name = 'archivo_entrega'
        verbose_name_plural = 'archivo_entregas'
        ordering = ['created_at']

    def __str__(self):
        return f"Archivo de entrega para {self.submission.student.username} en {self.submission.assignment.title}"