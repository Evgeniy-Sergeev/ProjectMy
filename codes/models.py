from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    ROLE_CHOICES = [
        ('student', 'Student'),
        ('teacher', 'Teacher'),
        ('admin', 'Administrator'),
    ]
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='student')

    groups = models.ManyToManyField(
        'auth.Group',
        related_name='custom_user_set',
        blank=True,
        help_text='The groups this user belongs to.',
        verbose_name='groups',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='custom_user_permissions_set',
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions',
    )


class Work(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="works")
    work_number = models.CharField(max_length=50)
    code = models.TextField()
    upload_date = models.DateTimeField(auto_now_add=True)


class Result(models.Model):
    work_1 = models.ForeignKey(Work, related_name='work_1', on_delete=models.CASCADE)
    work_2 = models.ForeignKey(Work, related_name='work_2', on_delete=models.CASCADE)
    similarity_percentage = models.FloatField()
    report = models.TextField()


class PostgresModel(models.Model):
    title = models.CharField(max_length=255)

    class Meta:
        app_label = 'postgres_app'


class SqliteModel(models.Model):
    name = models.CharField(max_length=255)

    class Meta:
        app_label = 'sqlite_app'
