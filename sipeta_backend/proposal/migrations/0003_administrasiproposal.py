# Generated by Django 4.0.10 on 2023-05-16 19:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('proposal', '0002_alter_proposal_options'),
    ]

    operations = [
        migrations.CreateModel(
            name='AdministrasiProposal',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status_pengajuan_proposal', models.BooleanField(default=True)),
            ],
        ),
    ]
