from django.db import models
from django.contrib.auth.models import AbstractUser

from django.contrib.auth.models import AbstractUser
from django.utils import timezone
import random

def generate_random_phone():
    # Generate last 4 digits randomly
    last_digits = ''.join([str(random.randint(0, 9)) for _ in range(4)])
    return f"38760306{last_digits}"


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
    phone_number_user = models.TextField(
        null=True, 
        blank=True,
        default='387603067074',
        unique=False  # Explicitly set unique=False
    )
    path_to_profile_picture = models.CharField(default = "", max_length=20, null=True)


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
    STATUS_CHOICES = [
        ('PREPARING', 'Preparing'),
        ('FINISHED', 'Finished'),
        ('CANCELED', 'Canceled'),
    ]
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='PREPARING'
    )

    origin_place_id = models.CharField(max_length=255, null=True)
    origin_latitude = models.FloatField(default=0)
    origin_longitude = models.FloatField(default=0)
    destination_place_id = models.CharField(max_length=255, null=True)
    destination_latitude = models.FloatField(default=0)
    destination_longitude = models.FloatField(default=0)
    distance_km = models.FloatField(default=0)
    duration_text = models.CharField(max_length=100, null=True)
    selected_route_index = models.IntegerField(default=0)
    selected_route_polyline = models.TextField(default='')


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
    

class RideApplication(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ride_applications')
    ride = models.ForeignKey(Ride, on_delete=models.CASCADE, related_name='applications')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    applied_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    message = models.TextField(blank=True, null=True)  # Optional message from applicant

    class Meta:
        unique_together = ('user', 'ride')  # Prevent duplicate applications
        ordering = ['-applied_at']
        verbose_name = 'Ride Application'
        verbose_name_plural = 'Ride Applications'

    def __str__(self):
        return f"{self.user.username}'s application for {self.ride.start} to {self.ride.end}"