import random
import string

from django.db import models
from django.conf import settings
# Create your models here.
class Curso(models.Model):
    class Status(models.TextChoices):
        ACTIVE = 'active', 'Active'
        INACTIVE = 'inactive', 'Inactive'

    name = models.CharField(max_length=255)
    description = models.TextField()
    period = models.CharField(max_length=100)

    teacher = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='cursos',
    )

    registration_code = models.CharField(max_length=8, unique=True, blank=True)
    status = models.CharField(
        max_length=8,
        choices=Status.choices,
        default=Status.ACTIVE,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'curso'
        verbose_name = 'curso'
        verbose_name_plural = 'cursos'
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.registration_code:
            self.registration_code = self.generate_code()
        super().save(*args, **kwargs)

    def generate_code(self):
        return ''.join(random.choices(string.ascii_letters + string.digits, k=8))

    def __str__(self):
        return self.name
