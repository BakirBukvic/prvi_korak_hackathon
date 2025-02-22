from django.db import models
from django.contrib.auth.models import AbstractUser

from django.contrib.auth.models import AbstractUser
from django.utils import timezone




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




class Ride(models.Model):
    start = models.CharField(max_length=50)
    end = models.CharField (max_length=50)
    distance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    travelers = models.IntegerField(default=1)
    duration = models.DurationField(null=True, blank=True)  
    created_on = models.DateTimeField(default=timezone.now)  # Changed from auto_now_add
    start_date = models.DateTimeField(default=timezone.now)
    arriving_date = models.DateTimeField(default=timezone.now)


class RouteDetails(models.Model):
    ride = models.OneToOneField(Ride, on_delete=models.CASCADE, related_name='route_details')
    origin_place_id = models.CharField(max_length=255)
    origin_latitude = models.FloatField()
    origin_longitude = models.FloatField()
    destination_place_id = models.CharField(max_length=255)
    destination_latitude = models.FloatField()
    destination_longitude = models.FloatField()
    distance_km = models.FloatField()
    duration_text = models.CharField(max_length=100)
    selected_route_index = models.IntegerField()
    selected_route_polyline = models.TextField()

    def __str__(self):
        return f"Route details for {self.ride}"



class UserRideAssociation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='rides')
    ride = models.ForeignKey(Ride, on_delete=models.CASCADE, related_name='riders')
    created_at = models.DateTimeField(auto_now_add=True)
    is_driver = models.BooleanField(default=False)

    class Meta:
        unique_together = ('user', 'ride')
        verbose_name = 'User Ride Association'
        verbose_name_plural = 'User Ride Associations'

    def __str__(self):
        return f"{self.user.username} - {self.ride.start} to {self.ride.end}"