# Generated by Django 4.1.1 on 2023-04-10 14:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0038_user_social_pfp_link'),
    ]

    operations = [
        migrations.AddField(
            model_name='notification',
            name='sender_social_pfp_link',
            field=models.CharField(blank=True, default='', max_length=256, null=True),
        ),
    ]