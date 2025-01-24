import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('password', models.CharField(max_length=255)),
                ('role', models.CharField(choices=[('student', 'Student'), ('teacher', 'Teacher')], max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='Work',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('work_number', models.CharField(max_length=50)),
                ('code', models.TextField()),
                ('upload_date', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='codes.user')),
            ],
        ),
        migrations.CreateModel(
            name='Result',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('similarity_percentage', models.FloatField()),
                ('report', models.TextField()),
                ('work_1', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='work_1', to='codes.work')),
                ('work_2', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='work_2', to='codes.work')),
            ],
        ),
    ]
