from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from healthdata.models import GlucoseEntry, SleepData, ActivityData
from datetime import date, timedelta
import random

User = get_user_model()

class Command(BaseCommand):
    help = "Load fake analytics data for testing (no CSV needed)."

    def handle(self, *args, **options):
        user, _ = User.objects.get_or_create(username="demo_user")
        today = date.today()

        # Clear old data
        GlucoseEntry.objects.filter(user=user).delete()
        SleepData.objects.filter(user=user).delete()
        ActivityData.objects.filter(user=user).delete()

        # Generate 20 days of fake data
        for i in range(20):
            d = today - timedelta(days=i)
            GlucoseEntry.objects.create(user=user, created_at=d, glucose_mg_dl=random.randint(120, 220))
            SleepData.objects.create(user=user, date=d, total_sleep_minutes=random.randint(300, 480))
            ActivityData.objects.create(user=user, date=d, steps=random.randint(4000, 12000))

        self.stdout.write(self.style.SUCCESS("✅ Demo analytics data loaded successfully!"))
