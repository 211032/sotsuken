# Generated by Django 5.1.2 on 2024-11-05 05:47

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Classroom',
            fields=[
                ('classroom_id', models.CharField(max_length=50, primary_key=True, serialize=False)),
                ('classroom_name', models.CharField(max_length=10, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Enrollment',
            fields=[
                ('enrollment_id', models.AutoField(primary_key=True, serialize=False)),
                ('class_identifier', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='Student',
            fields=[
                ('email', models.EmailField(max_length=254, primary_key=True, serialize=False)),
                ('class_name', models.CharField(max_length=100)),
                ('name', models.CharField(max_length=100)),
                ('password', models.CharField(max_length=128)),
            ],
        ),
        migrations.CreateModel(
            name='Subject',
            fields=[
                ('subject_id', models.AutoField(primary_key=True, serialize=False)),
                ('subject_name', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Teacher',
            fields=[
                ('teacher_id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100)),
                ('password', models.CharField(max_length=128)),
                ('romanized_last_name', models.CharField(max_length=100)),
                ('roll', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Equipment',
            fields=[
                ('device_id', models.CharField(max_length=10, primary_key=True, serialize=False)),
                ('minor', models.IntegerField()),
                ('location', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='application.classroom')),
            ],
        ),
        migrations.CreateModel(
            name='Attendance',
            fields=[
                ('attendance_id', models.CharField(max_length=50, primary_key=True, serialize=False)),
                ('period', models.IntegerField()),
                ('start_time', models.TimeField()),
                ('end_time', models.TimeField()),
                ('attendance_time', models.TimeField(blank=True, null=True)),
                ('exit_time', models.TimeField(blank=True, null=True)),
                ('attendance_status', models.CharField(choices=[('present', '出席'), ('absent', '欠席'), ('late', '遅刻'), ('leave_early', '早退'), ('not_attended', '退席')], max_length=20)),
                ('classroom', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='application.classroom')),
                ('enrollment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='application.enrollment')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='application.student')),
            ],
        ),
        migrations.AddField(
            model_name='enrollment',
            name='subject',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='application.subject'),
        ),
        migrations.AddField(
            model_name='enrollment',
            name='instructor_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='application.teacher'),
        ),
        migrations.CreateModel(
            name='Timetable',
            fields=[
                ('email', models.EmailField(max_length=254, primary_key=True, serialize=False)),
                ('date', models.DateField()),
                ('is_special_class', models.BooleanField(default=False)),
                ('period1', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='timetable_period1', to='application.attendance')),
                ('period2', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='timetable_period2', to='application.attendance')),
                ('period3', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='timetable_period3', to='application.attendance')),
                ('period4', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='timetable_period4', to='application.attendance')),
            ],
            options={
                'unique_together': {('email', 'date')},
            },
        ),
    ]
