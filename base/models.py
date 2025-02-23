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
    points = models.IntegerField(default=0)  # Points required to reach this level
    svg_path = models.TextField(blank=True, null=True)
    level = models.IntegerField(default=0)

    def save(self, *args, **kwargs):
        self.svg_path = f"{self.level}.svg"
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['points']  # Order levels by required points


        
class User(AbstractUser):
    level = models.ForeignKey(UserLevel, on_delete=models.SET_NULL, null=True)
    km_passed = models.IntegerField(default=0)
    number_of_rides = models.IntegerField(default=0)
    penguins_saved = models.IntegerField(default=0)
    co2_saved = models.FloatField(default=0)  # Stored in kilograms

    def calculate_points(self):
        return round(self.km_passed * 0.1)  # 0.1 points per km

    def calculate_co2_saved(self):
        # 130g (0.13kg) CO2 per km
        return round(self.km_passed * 0.13, 2)  # Returns kg of CO2 saved
    
    def update_stats(self, new_km):
        """Update user stats when completing a ride"""
        self.km_passed += new_km
        self.number_of_rides += 1
        self.penguins_saved = int(self.km_passed // 100)  # Explicitly convert to int
        self.co2_saved = self.calculate_co2_saved()
        self.save()
        self.update_level()

    def update_level(self):
        """Update user level based on current points"""
        current_points = self.calculate_points()
        new_level = UserLevel.objects.filter(
            points__lte=current_points
        ).order_by('-points').first()
        
        if new_level and (not self.level or self.level.points < new_level.points):
            self.level = new_level
            self.save()

class Penguin(models.Model):
    RARITY_CHOICES = [
        ('COMMON', 'Common'),
        ('RARE', 'Rare'),
        ('EPIC', 'Epic'),
        ('LEGENDARY', 'Legendary'),
    ]

    penguin_name = models.CharField(max_length=100)
    svg_direction = models.CharField(max_length=255)  # Path to SVG file
    rarity = models.CharField(
        max_length=10,
        choices=RARITY_CHOICES,
        default='COMMON'
    )

    def __str__(self):
        return f"{self.penguin_name} ({self.get_rarity_display()})"

    class Meta:
        verbose_name = 'Penguin'
        verbose_name_plural = 'Penguins'

    @property
    def rarity_color(self):
        return {
            'COMMON': '#808080',     # Gray
            'RARE': '#0077be',       # Blue
            'EPIC': '#9b30ff',       # Purple
            'LEGENDARY': '#ffd700',   # Gold
        }.get(self.rarity, '#808080')

class PenguinCollected(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='collected_penguins')
    penguin = models.ForeignKey(Penguin, on_delete=models.CASCADE)
    is_collected = models.BooleanField(default=False)
    collected_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'penguin')  # Each user can collect each penguin only once
        verbose_name = 'Collected Penguin'
        verbose_name_plural = 'Collected Penguins'

    def __str__(self):
        return f"{self.user.username} - {self.penguin.penguin_name}"

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


class GiftCard(models.Model):
    STATUS_CHOICES = [
        ('AVAILABLE', 'Available'),
        ('CLAIMED', 'Claimed'),
        ('EXPIRED', 'Expired')
    ]
    
    code = models.CharField(max_length=50, unique=True)
    user = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='gift_cards'
    )
    station_place_id = models.CharField(max_length=255)
    station_name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    claimed_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField()
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='AVAILABLE'
    )
    
    class Meta:
        verbose_name = 'Gift Card'
        verbose_name_plural = 'Gift Cards'
        
    def __str__(self):
        return f"Gift Card {self.code} - {self.get_status_display()}"