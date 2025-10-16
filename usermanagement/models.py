# usermanagement/models.py
from django.conf import settings
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model

# ---------------------------------------------------------------------
# CustomUser: used for consent tracking
# ---------------------------------------------------------------------
class CustomUser(models.Model):
    """
    Custom user model for consent management.
    """
    username = models.CharField(max_length=150, unique=True)
    data_sharing_consent = models.BooleanField(
        default=False,
        verbose_name="Consent to share anonymized health data for research/insurance purposes.",
    )
    consent_timestamp = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.username

# ---------------------------------------------------------------------
# Profile model (already existing)
# ---------------------------------------------------------------------
class Profile(models.Model):
    """
    Stores additional user information beyond the built-in Django User model.
    Each User has one Profile (created automatically).
    """
    SEX_CHOICES = [
        ("male", "Male"),
        ("female", "Female"),
        ("other", "Other / Prefer not to say"),
    ]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile",
    )
    age = models.PositiveIntegerField(null=True, blank=True)
    height_cm = models.PositiveIntegerField(null=True, blank=True)
    weight_kg = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    sex = models.CharField(max_length=12, choices=SEX_CHOICES, null=True, blank=True)

    def __str__(self):
        return f"Profile({self.user.username})"

    @property
    def bmi(self):
        """Compute BMI if height/weight are set."""
        if self.height_cm and self.weight_kg:
            height_m = self.height_cm / 100
            return round(float(self.weight_kg) / (height_m ** 2), 1)
        return None


# ---------------------------------------------------------------------
# Signals: ensure a Profile always exists for every User
# ---------------------------------------------------------------------

User = get_user_model()

@receiver(post_save, sender=User)
def ensure_profile_exists(sender, instance, created, **kwargs):
    """
    Always ensure a Profile exists for the user.
    We use get_or_create (safe) instead of touching instance.profile directly.
    """
    Profile.objects.get_or_create(user=instance)
