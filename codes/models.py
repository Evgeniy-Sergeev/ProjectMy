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


class Lesson(models.Model):
    title = models.CharField(max_length=100)

    def __str__(self):
        return self.title


class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)  # Связываем с User, добавлен null и blank для совместимости
    full_name = models.CharField(max_length=200)

    def __str__(self):
        return self.full_name


class Submission(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    code = models.TextField()
    submission_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Submission by {self.student.full_name} for lesson {self.lesson.title}"


class Work(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="works")
    work_number = models.CharField(max_length=50)
    code = models.TextField()
    upload_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Work {self.work_number} by {self.user.username}"


from difflib import SequenceMatcher

class Result(models.Model):
    work_1 = models.ForeignKey(Work, related_name='work_1', on_delete=models.CASCADE)
    work_2 = models.ForeignKey(Work, related_name='work_2', on_delete=models.CASCADE)
    similarity_percentage = models.FloatField()
    report = models.TextField()

    def __str__(self):
        return f"Result between Work {self.work_1.work_number} and Work {self.work_2.work_number}"

    def save(self, *args, **kwargs):
        similarity = self.calculate_similarity(self.work_1.code, self.work_2.code)
        self.similarity_percentage = similarity
        self.report = f"Similarity: {similarity}%"
        super().save(*args, **kwargs)

def calculate_similarity(self, code1, code2):
        return SequenceMatcher(None, code1, code2).ratio() * 100

class PostgresModel(models.Model):
    title = models.CharField(max_length=255)

    class Meta:
        app_label = 'postgres_app'

    def __str__(self):
        return self.title


class SqliteModel(models.Model):
    name = models.CharField(max_length=255)

    class Meta:
        app_label = 'sqlite_app'

    def __str__(self):
        return self.name
