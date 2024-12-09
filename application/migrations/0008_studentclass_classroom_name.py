# Generated by Django 5.1.2 on 2024-12-09 06:13

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('application', '0007_remove_studentclass_classroom_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='studentclass',
            name='classroom_name',
            field=models.ForeignKey(default='01', on_delete=django.db.models.deletion.CASCADE, to='application.classroom'),
        ),
    ]
