# Generated by Django 4.1.1 on 2023-04-10 17:23

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0041_blogcomments_blog'),
    ]

    operations = [
        migrations.RenameField(
            model_name='blogcomments',
            old_name='content',
            new_name='comment',
        ),
    ]
