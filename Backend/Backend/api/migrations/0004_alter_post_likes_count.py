# Generated by Django 4.1.1 on 2023-03-05 21:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0003_post_likes_post_likes_count'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='likes_count',
            field=models.IntegerField(default=0),
        ),
    ]
