from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import UserLevel, Ride,UserRideAssociation

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
        # Check if this is an existing ride (not a new one)
        if instance.pk:
            old_instance = Ride.objects.get(pk=instance.pk)
            
            # Check if status is being changed to FINISHED
            if old_instance.status != 'FINISHED' and instance.status == 'FINISHED':
                # Get all passengers including driver
                passengers = UserRideAssociation.objects.filter(
                    ride=instance
                ).select_related('user')
                
                # Update each passenger's stats
                for passenger in passengers:
                    user = passenger.user
                    user.km_passed += instance.distance_km
                    user.number_of_rides += 1
                    user.save()  # This will trigger the level update signal
    except Ride.DoesNotExist:
        pass