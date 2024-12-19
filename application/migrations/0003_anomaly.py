# Generated by Django 5.1.3 on 2024-12-18 06:00

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('application', '0002_remove_timetable_timetable_id_timetable_id'),
    ]

    operations = [
        migrations.CreateModel(
            name='Anomaly',
            fields=[
                ('anomaly_id', models.AutoField(primary_key=True, serialize=False)),
                ('attendance_time', models.TimeField()),
                ('exit_time', models.TimeField()),
                ('attendance_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='application.attendance')),
                ('classroom', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='application.classroom')),
            ],
        ),
    ]
