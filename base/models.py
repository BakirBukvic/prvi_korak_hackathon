from django.db import models
from django.contrib.auth.models import AbstractUser

class UserLevel(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField(blank=True, null=True)
    points = models.IntegerField(default=0)
    svg_path = models.TextField(blank=True, null=True)
    level = models.IntegerField(default=0)
    def __str__(self):
        return self.name
    

class User(AbstractUser):
    level = models.ForeignKey(UserLevel, on_delete=models.SET_NULL, null=True)
    km_passed = models.IntegerField(default=0)
    number_of_rides = models.IntegerField(default=0)
    profile_description = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'