from datetime import timezone

from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.
class SoftDeleteManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(deleted_at__isnull=True)

class SoftDeleteModel(models.Model):
    deleted_at = models.DateTimeField(blank=True, null=True)

    objects = SoftDeleteManager()
    all_objects = models.Manager()

    class Meta:
        abstract = True

    def soft_delete(self):
        self.deleted_at = timezone.now()
        self.save()

    def restore(self):
        self.deleted_at = None
        self.save()

class User(AbstractUser, SoftDeleteModel):

    class Roles(models.TextChoices):
        TEACHER = 'teacher', 'teacher'
        STUDENT = 'student', 'student'

    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    telephone = models.CharField(max_length=11, blank=True)

    rol = models.CharField(
        max_length=10,
        choices=Roles.choices,
        default=Roles.STUDENT
    )

    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        db_table = 'user'
        verbose_name = 'user'
        verbose_name_plural = 'users'
        ordering = ['-date_joined']

    def __str__(self):
        return self.email
