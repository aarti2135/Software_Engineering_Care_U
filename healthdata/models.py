from django.db import models

# Create your models here.

from django.db import models
from django.conf import settings

# ACTUAL HEALTH DATA STORAGE (your core responsibility)
class HealthData(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    device_type = models.CharField(max_length=100)
    steps = models.IntegerField()
    calories_burned = models.IntegerField()
    heart_rate = models.IntegerField(null=True, blank=True)
    sleep_minutes = models.IntegerField(null=True, blank=True)
    recorded_date = models.DateTimeField(auto_now_add=True)

# GRANULAR PRIVACY CONTROLS (enhancement of your story)
class HealthPrivacySettings(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    share_steps = models.BooleanField(default=False)
    share_heart_rate = models.BooleanField(default=False)
    share_sleep_data = models.BooleanField(default=False)
    share_calories = models.BooleanField(default=False)
