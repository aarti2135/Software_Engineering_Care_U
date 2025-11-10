from django.conf import settings
from django.db import models
from django.utils import timezone
from datetime import timedelta


class DismissedHighlight(models.Model):
    """
    Stores when a user dismisses a highlight so we can hide it for 48h.
    The 'key' identifies the pattern type (e.g., 'high_glucose', 'low_sleep', 'activity_drop').
    """
    KEY_CHOICES = [
        ('high_glucose', 'High Glucose'),
        ('low_sleep', 'Low Sleep'),
        ('activity_drop', 'Activity Drop'),
    ]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    key = models.CharField(max_length=32, choices=KEY_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    hidden_until = models.DateTimeField()

    class Meta:
        indexes = [
            models.Index(fields=['user', 'key', 'hidden_until']),
        ]

    def __str__(self):
        return f"{self.user} - {self.key} hidden until {self.hidden_until:%Y-%m-%d %H:%M}"

    @classmethod
    def is_hidden(cls, user, key):
        now = timezone.now()
        return cls.objects.filter(user=user, key=key, hidden_until__gt=now).exists()

    @classmethod
    def dismiss_for_48h(cls, user, key):
        now = timezone.now()
        inst, _ = cls.objects.get_or_create(
            user=user, key=key,
            defaults={'hidden_until': now + timedelta(hours=48)}
        )
        if inst.hidden_until <= now:  # if expired, push again
            inst.hidden_until = now + timedelta(hours=48)
            inst.save()
        return inst