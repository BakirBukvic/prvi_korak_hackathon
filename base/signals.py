from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import UserLevel, Ride,UserRideAssociation, Penguin, PenguinCollected
import random


User = get_user_model()

@receiver(pre_save, sender=User)
def check_level_update(sender, instance, **kwargs):
    if instance.pk:  # Only for existing users
        try:
            old_instance = User.objects.get(pk=instance.pk)
            if old_instance.km_passed != instance.km_passed:
                instance.update_level()
        except User.DoesNotExist:
            pass

@receiver(post_save, sender=User)
def ensure_user_has_level(sender, instance, created, **kwargs):
    if created or not instance.level:
        default_level = UserLevel.objects.filter(level=0).first()
        if not default_level:
            default_level = UserLevel.objects.create(
                level=0,
                name='Beginner',
                description='Starting level',
                points=0
            )
        instance.level = default_level
        instance.save()



@receiver(pre_save, sender=Ride)
def handle_ride_finish(sender, instance, **kwargs):
    try:
        if instance.pk:
            old_instance = Ride.objects.get(pk=instance.pk)
            
            # Check if ride status changed to FINISHED
            if old_instance.status != 'FINISHED' and instance.status == 'FINISHED':
                passengers = UserRideAssociation.objects.filter(
                    ride=instance
                ).select_related('user')
                
                for passenger in passengers:
                    user = passenger.user
                    # Use distance instead of distance_km - this was the issue
                    new_km = float(instance.distance)  # Convert to float
                    user.update_stats(new_km)
    except Ride.DoesNotExist:
        pass


User = get_user_model()

@receiver(pre_save, sender=User)
def update_penguins_saved(sender, instance, **kwargs):
    """Calculate penguins saved based on kilometers passed"""
    if instance.pk:  # Only for existing users
        old_instance = User.objects.get(pk=instance.pk)
        if old_instance.km_passed != instance.km_passed:
            # Calculate penguins saved (1 penguin per 100km)
            instance.penguins_saved = instance.km_passed // 100

@receiver(pre_save, sender=User)
def create_penguin_collection(sender, instance, **kwargs):
    """Create PenguinCollected entries when user gets new penguins"""
    if instance.pk:
        old_instance = User.objects.get(pk=instance.pk)
        old_penguins = int(old_instance.penguins_saved)
        new_penguins = int(instance.penguins_saved)
        
        # Calculate difference for new penguins only
        penguin_difference = max(0, new_penguins - old_penguins)
        
        if penguin_difference > 0:
            available_penguins = Penguin.objects.all()
            
            if available_penguins.exists():
                for _ in range(penguin_difference):
                    random_penguin = random.choice(available_penguins)
                    PenguinCollected.objects.get_or_create(
                        user=instance,
                        penguin=random_penguin,
                        defaults={'is_collected': False}
                    )



@receiver(post_save, sender=PenguinCollected)
def update_penguin_notifications(sender, instance, **kwargs):
    """Update notification count when penguin collection status changes"""
    uncollected_count = PenguinCollected.objects.filter(
        user=instance.user,
        is_collected=False
    ).count()
    
    # Store the count in the user's session
    if hasattr(instance.user, 'session'):
        instance.user.session['uncollected_penguins'] = uncollected_count