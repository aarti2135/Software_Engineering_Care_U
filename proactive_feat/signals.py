from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import VitalReading, Alert
from .rules import evaluate_threshold

@receiver(post_save, sender=VitalReading)
def create_threshold_alert(sender, instance, created, **kwargs):
    if not created:
        return
    verdict = evaluate_threshold(instance.kind, instance.value)
    if verdict:
        Alert.objects.create(
            user=instance.user,
            alert_type="threshold",
            message=f"Abnormal {verdict} at {instance.measured_at:%Y-%m-%d %H:%M}",
        )
