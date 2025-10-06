# usermanagement/signals.py
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Profile

User = get_user_model()

@receiver(post_save, sender=User)
def ensure_profile_exists(sender, instance, created, **kwargs):
    # Create a profile when a new user is created
    if created:
        Profile.objects.get_or_create(user=instance)
    else:
        # For existing users, make sure there's a profile too
        Profile.objects.get_or_create(user=instance)
