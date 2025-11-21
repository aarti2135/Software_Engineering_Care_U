#!/usr/bin/env python
"""
Quick script to add test data for the home dashboard
Run this with: python add_test_data.py
"""

import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'CareU.settings')
django.setup()

from django.contrib.auth import get_user_model
from healthdata.models import ActivityData, HealthMetrics, Goal
from django.utils import timezone

User = get_user_model()


def add_test_data():
    """Add test data for the home dashboard"""

    # Get the first user (or create if none exist)
    user = User.objects.first()
    if not user:
        print("❌ No users found. Please create a user first.")
        return

    print(f"✅ Adding test data for user: {user.username}")

    today = timezone.localdate()

    # 1. Add today's activity (steps) - FIX for duplicates
    print("\n📊 Processing ActivityData...")

    # Delete any existing records for today to avoid duplicates
    existing_activities = ActivityData.objects.filter(user=user, date=today)
    if existing_activities.exists():
        count = existing_activities.count()
        existing_activities.delete()
        print(f"   🗑️  Removed {count} existing ActivityData record(s) for today")

    # Now create a fresh record
    activity = ActivityData.objects.create(
        user=user,
        date=today,
        steps=7500,
        activity_type='walking',
        active_minutes=45,
        calories_burned=350
    )
    print(f"✅ ActivityData: Created - {activity.steps} steps")

    # 2. Add heart rate metrics - FIX for duplicates
    print("\n❤️  Processing HealthMetrics...")

    # Get or create the latest metrics
    latest_metric = HealthMetrics.objects.filter(user=user).order_by('-logged_at').first()

    if latest_metric:
        # Update the existing one
        latest_metric.heart_rate_resting = 68
        latest_metric.weight_kg = 70.5
        latest_metric.save()
        print(f"✅ HealthMetrics: Updated - {latest_metric.heart_rate_resting} bpm")
    else:
        # Create new one
        metrics = HealthMetrics.objects.create(
            user=user,
            logged_at=timezone.now(),
            heart_rate_resting=68,
            weight_kg=70.5
        )
        print(f"✅ HealthMetrics: Created - {metrics.heart_rate_resting} bpm")

    # 3. Add an active goal - FIX for duplicates
    print("\n🎯 Processing Goals...")

    # Check if goal already exists
    existing_goal = Goal.objects.filter(
        user=user,
        title="Walk 10,000 steps daily"
    ).first()

    if existing_goal:
        # Update existing goal
        existing_goal.goal_type = 'steps'
        existing_goal.frequency = 'daily'
        existing_goal.target_value = 10000
        existing_goal.current_value = 7500
        existing_goal.status = 'active'
        existing_goal.notes = 'Maintain a consistent walking habit to improve stamina and overall health.'
        existing_goal.save()
        print(f"✅ Goal: Updated - {existing_goal.title}")
    else:
        # Create new goal
        goal = Goal.objects.create(
            user=user,
            title="Walk 10,000 steps daily",
            goal_type='steps',
            frequency='daily',
            target_value=10000,
            current_value=7500,
            status='active',
            notes='Maintain a consistent walking habit to improve stamina and overall health.'
        )
        print(f"✅ Goal: Created - {goal.title}")

    print("\n" + "=" * 60)
    print("🎉 Test data added successfully!")
    print("📊 Now refresh your home dashboard to see the changes.")
    print("=" * 60)


if __name__ == "__main__":
    add_test_data()