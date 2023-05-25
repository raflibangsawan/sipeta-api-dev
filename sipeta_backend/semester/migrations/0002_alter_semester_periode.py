# Generated by Django 4.0.10 on 2023-05-24 19:34

from django.db import migrations, models
import sipeta_backend.semester.validators


class Migration(migrations.Migration):

    dependencies = [
        ('semester', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='semester',
            name='periode',
            field=models.CharField(default='2022/2023', max_length=9, validators=[sipeta_backend.semester.validators.validate_periode_semester]),
        ),
    ]