# Generated by Django 5.1.2 on 2025-02-22 01:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='userlevel',
            name='level',
            field=models.IntegerField(default=0),
        ),
    ]
