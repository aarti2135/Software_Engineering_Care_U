from django.db import models

class CustomUser(models.Model):
    """
    Custom user model for CUFitness.

    Added fields:
    - data_sharing_consent: Stores explicit consent for sharing PIHD with third parties.
    """
    username = models.CharField()
    # data_sharing_consent = models.BooleanField(
    #     default=False,
    #     verbose_name="Consent to share anonymized health data for research/insurance purposes."
    # )

    def __str__(self):
        return self.username