# Generated by Django 4.1.1 on 2023-03-13 16:43

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0020_alter_post_dislikes_alter_post_likes'),
    ]

    operations = [
        migrations.DeleteModel(
            name='PostImages',
        ),
    ]
