# Generated by Django 5.1.2 on 2025-02-22 09:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0009_user_phone_number_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='path_to_profile_picture',
            field=models.CharField(default='', max_length=20),
        ),
    ]
