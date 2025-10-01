from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    """
    Custom user model for CUFtness.

    Added fields:
    - data_sharing_consent: Stores explicit consent for sharing PIHD with third parties.
    """
    data_sharing_consent = models.BooleanField(
        default=False,
        verbose_name="Consent to share anonymized health data for research/insurance purposes."
    )

    def __str__(self):
        return self.username