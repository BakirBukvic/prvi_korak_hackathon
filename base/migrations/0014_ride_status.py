# Generated by Django 5.1.2 on 2025-02-22 13:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0013_rideapplication'),
    ]

    operations = [
        migrations.AddField(
            model_name='ride',
            name='status',
            field=models.CharField(choices=[('PREPARING', 'Preparing'), ('FINISHED', 'Finished')], default='PREPARING', max_length=10),
        ),
    ]
