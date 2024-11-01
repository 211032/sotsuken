# Generated by Django 5.1.2 on 2024-11-01 05:58

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('application', '0005_rename_major_equipment_macaddress_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Classroom',
            fields=[
                ('classroom_id', models.CharField(max_length=50, primary_key=True, serialize=False)),
                ('classroom_name', models.CharField(max_length=10, unique=True)),
            ],
        ),
        migrations.RemoveField(
            model_name='attendance',
            name='classroom_id',
        ),
        migrations.RemoveField(
            model_name='attendance',
            name='student_id',
        ),
        migrations.AddField(
            model_name='attendance',
            name='student',
            field=models.ForeignKey(default=23, on_delete=django.db.models.deletion.CASCADE, to='application.student'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='attendance',
            name='attendance_id',
            field=models.CharField(max_length=50, primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='enrollment',
            name='instructor_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='application.teacher'),
        ),
        migrations.AlterField(
            model_name='timetable',
            name='period1',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='timetable_period1', to='application.attendance'),
        ),
        migrations.AlterField(
            model_name='timetable',
            name='period2',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='timetable_period2', to='application.attendance'),
        ),
        migrations.AlterField(
            model_name='timetable',
            name='period3',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='timetable_period3', to='application.attendance'),
        ),
        migrations.AlterField(
            model_name='timetable',
            name='period4',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='timetable_period4', to='application.attendance'),
        ),
        migrations.AddField(
            model_name='attendance',
            name='classroom',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='application.classroom'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='equipment',
            name='location',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='application.classroom'),
        ),
    ]
