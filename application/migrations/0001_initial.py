# Generated by Django 5.1.2 on 2024-10-21 05:24

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Student',
            fields=[
                ('email', models.EmailField(max_length=254, primary_key=True, serialize=False)),
                ('class_name', models.CharField(max_length=100)),
                ('name', models.CharField(max_length=100)),
                ('password', models.CharField(max_length=128)),
            ],
        ),
    ]
