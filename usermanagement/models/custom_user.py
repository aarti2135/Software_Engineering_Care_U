from django.db import models
#from django.utils import timezone


class CustomUser(models.Model):
    """
    Custom user model for CUFitness.

    Added fields:
    - data_sharing_consent: Stores explicit consent for sharing PIHD with third parties.
    - consent_date: Stores the date when the user gave or updated their consent.
    """
    username = models.CharField(max_length=150)
    data_sharing_consent = models.BooleanField(
        default=False,
        verbose_name="Consent to share anonymized health data for research/insurance purposes."
    )


    def __str__(self):
        return self.username
