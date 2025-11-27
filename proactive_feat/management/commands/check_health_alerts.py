from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from proactive_feat.models import VitalReading, Alert
from proactive_feat.rules import last_log_older_than

User = get_user_model()

class Command(BaseCommand):
    help = "Detect missed logs and repeated abnormal patterns"

    def handle(self, *args, **opts):
        for user in User.objects.all():
            gqs = VitalReading.objects.filter(user=user, kind="glucose")
            if last_log_older_than(gqs, hours=24):
                Alert.objects.create(
                    user=user,
                    alert_type="missed_log",
                    message="No glucose log in the last 24 hours."
                )
            recent = timezone.now() - timedelta(hours=48)
            if Alert.objects.filter(user=user, alert_type="threshold", created_at__gte=recent).count() >= 3:
                Alert.objects.create(
                    user=user,
                    alert_type="trend",
                    message="Repeated abnormal readings detected. Consider contacting your doctor."
                )
