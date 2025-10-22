from django.conf import settings
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model

# Get Django's User model
User = get_user_model()


# ---------------------------------------------------------------------
# Profile model - Extended user information + consent tracking
# ---------------------------------------------------------------------
class Profile(models.Model):
    """
    Stores additional user information beyond the built-in Django User model.
    Each User has one Profile (created automatically via signals).
    NOW INCLUDES: consent tracking (previously in CustomUser)
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

    # Existing profile fields
    age = models.PositiveIntegerField(null=True, blank=True)
    height_cm = models.PositiveIntegerField(null=True, blank=True)
    weight_kg = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    sex = models.CharField(max_length=12, choices=SEX_CHOICES, null=True, blank=True)

    # ✅ NEW: Consent fields (moved from CustomUser)
    data_sharing_consent = models.BooleanField(
        default=False,
        verbose_name="Consent to share anonymized health data for research/insurance purposes",
    )
    consent_timestamp = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the user last updated their consent preference"
    )

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
# Signal: ensure a Profile always exists for every User
# ---------------------------------------------------------------------
@receiver(post_save, sender=User)
def ensure_profile_exists(sender, instance, created, **kwargs):
    """
    Always ensure a Profile exists for the user.
    We use get_or_create (safe) instead of touching instance.profile directly.
    """
    Profile.objects.get_or_create(user=instance)


# ---------------------------------------------------------------------
# ProviderAlert model for Epic 3
# ---------------------------------------------------------------------
class ProviderAlert(models.Model):
    """
    Stores AI-generated alerts for healthcare providers
    when concerning patient data patterns are detected.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="provider_alerts"
    )
    alert_type = models.CharField(max_length=100)
    message = models.TextField()
    severity = models.CharField(max_length=20, choices=[
        ("low", "Low"),
        ("moderate", "Moderate"),
        ("high", "High"),
    ])
    created_at = models.DateTimeField(auto_now_add=True)
    reviewed = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.alert_type} ({self.severity}) for {self.user.username}"


# ❌ DELETED: CustomUser class
# All consent functionality moved to Profile model

