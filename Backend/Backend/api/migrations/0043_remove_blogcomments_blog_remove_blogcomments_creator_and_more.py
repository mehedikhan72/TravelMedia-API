# Generated by Django 4.1.1 on 2023-04-10 19:28

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0042_rename_content_blogcomments_comment'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='blogcomments',
            name='blog',
        ),
        migrations.RemoveField(
            model_name='blogcomments',
            name='creator',
        ),
        migrations.DeleteModel(
            name='Blog',
        ),
        migrations.DeleteModel(
            name='BlogComments',
        ),
    ]