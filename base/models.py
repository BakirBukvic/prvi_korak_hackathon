from django.db import models
from django.contrib.auth.models import User

class UserLevel(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField(blank=True, null=True)
    points = models.IntegerField(default=0)
    svg_path = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    level = models.ForeignKey(UserLevel, on_delete=models.SET_NULL, null=True)
    km_passed = models.IntegerField(default=0)
    number_of_rides = models.IntegerField(default=0)
    profile_description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.user.username}'s profile"

    class Meta:
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'