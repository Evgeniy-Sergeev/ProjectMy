# Generated by Django 5.1.5 on 2025-01-24 14:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("codes", "0004_lesson_student_submission"),
    ]

    operations = [
        migrations.AlterField(
            model_name="student",
            name="full_name",
            field=models.CharField(max_length=200),
        ),
    ]
