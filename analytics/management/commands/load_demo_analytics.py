from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model
from healthdata.models import GlucoseEntry, SleepData, ActivityData
from datetime import date, timedelta
import random

User = get_user_model()


class Command(BaseCommand):
    help = "Load fake analytics data for testing (no CSV needed)."

    def add_arguments(self, parser):
        parser.add_argument(
            '--username',
            type=str,
            help='Username to create data for (defaults to first active user)'
        )
        parser.add_argument(
            '--days',
            type=int,
            default=20,
            help='Number of days of data to generate (default: 20)'
        )

    def handle(self, *args, **options):
        # Get the target user
        username = options.get('username')

        if username:
            try:
                user = User.objects.get(username=username)
                self.stdout.write(f"Creating data for user: {username}")
            except User.DoesNotExist:
                raise CommandError(f'User "{username}" does not exist.')
        else:
            # Use first active user (most likely the logged-in user)
            user = User.objects.filter(is_active=True).order_by('id').first()
            if not user:
                raise CommandError('No active users found. Please create a user first.')
            self.stdout.write(f"Creating data for user: {user.username}")

        today = date.today()
        days = options.get('days', 20)

        # Clear old data
        GlucoseEntry.objects.filter(user=user).delete()
        SleepData.objects.filter(user=user).delete()
        ActivityData.objects.filter(user=user).delete()
        self.stdout.write("Cleared existing data...")

        # Generate fake data
        for i in range(days):
            d = today - timedelta(days=i)

            # Glucose: realistic range 95-180 mg/dL, with some high readings
            glucose = random.randint(95, 180)
            if i < 3:  # Last 3 days have some high readings
                glucose = random.randint(180, 220)

            GlucoseEntry.objects.create(
                user=user,
                created_at=d,
                glucose_mg_dl=glucose
            )

            # Sleep: 5-8 hours (300-480 minutes)
            sleep_minutes = random.randint(300, 480)
            SleepData.objects.create(
                user=user,
                date=d,
                total_sleep_minutes=sleep_minutes
            )

            # Steps: 4000-12000
            steps = random.randint(4000, 12000)
            ActivityData.objects.create(
                user=user,
                date=d,
                steps=steps
            )

        self.stdout.write(self.style.SUCCESS(
            f"✅ Successfully created {days} days of demo analytics data for '{user.username}'!"
        ))