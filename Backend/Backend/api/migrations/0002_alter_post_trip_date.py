# Generated by Django 4.1.1 on 2023-03-04 01:21

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='trip_date',
            field=models.DateField(default=datetime.date.today),
        ),
    ]
