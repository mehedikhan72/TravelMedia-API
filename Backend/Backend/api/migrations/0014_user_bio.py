# Generated by Django 4.1.1 on 2023-03-12 10:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0013_user_gender_user_location_user_phone_number'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='bio',
            field=models.CharField(blank=True, max_length=256),
        ),
    ]
