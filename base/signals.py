from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import UserLevel

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