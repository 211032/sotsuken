# Generated by Django 5.1.2 on 2024-12-05 02:16

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('application', '0002_remove_attendance_period'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='attendance',
            name='student',
        ),
    ]
