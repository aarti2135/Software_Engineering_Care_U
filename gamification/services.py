from django.utils import timezone
from django.db.models import Count, Q
from datetime import timedelta
from .models import Badge, UserBadge, UserStreak, WeeklyProgress
from healthdata.models import NutritionEntry, Goal, ActivityData, SleepData, HealthMetrics


class GamificationService:
    """Handle all gamification logic"""

    def __init__(self, user):
        self.user = user
        self.streak, _ = UserStreak.objects.get_or_create(user=user)

    def _get_all_activity_dates(self):
        """Get all dates where user logged any health data"""
        dates = set()

        # Get dates from various models
        nutrition_dates = NutritionEntry.objects.filter(
            user=self.user
        ).values_list('logged_at', flat=True)
        dates.update(nutrition_dates)

        activity_dates = ActivityData.objects.filter(
            user=self.user
        ).values_list('date', flat=True)
        dates.update(activity_dates)

        sleep_dates = SleepData.objects.filter(
            user=self.user
        ).values_list('date', flat=True)
        dates.update(sleep_dates)

        metrics_dates = HealthMetrics.objects.filter(
            user=self.user
        ).values_list('logged_at', flat=True)
        # Convert datetime to date for metrics
        dates.update([dt.date() if hasattr(dt, 'date') else dt for dt in metrics_dates])

        return sorted(dates, reverse=True)

    def process_activity(self):
        """Process health data activities to update streaks"""
        # Get all health data dates
        health_dates = self._get_all_activity_dates()

        if not health_dates:
            return

        # Calculate current streak
        today = timezone.localdate()
        current_streak = 0
        check_date = today

        for data_date in health_dates:
            if data_date == check_date:
                current_streak += 1
                check_date -= timedelta(days=1)
            elif data_date < check_date:
                break

        # Update streak
        self.streak.current_streak = current_streak
        self.streak.longest_streak = max(self.streak.longest_streak, current_streak)
        self.streak.total_activities = len(health_dates)
        self.streak.last_activity_date = health_dates[0] if health_dates else None
        self.streak.save()

        # Update weekly progress and check badges
        self._update_weekly_progress()
        self._check_and_award_badges()

    def record_activity(self):
        """
        Call this whenever user logs data (nutrition, activity, etc.)
        Updates streak, checks badges, updates weekly progress
        """
        # Update streak
        self.streak.update_streak()

        # Update weekly progress
        self._update_weekly_progress()

        # Check and award badges
        self._check_and_award_badges()

        return {
            'streak': self.streak.current_streak,
            'new_badges': self._get_newly_earned_badges()
        }

    def _update_weekly_progress(self):
        """Update current week's progress"""
        today = timezone.localdate()
        week_start = today - timedelta(days=today.weekday())  # Monday

        progress, created = WeeklyProgress.objects.get_or_create(
            user=self.user,
            week_start=week_start,
            defaults={'goal_target': 7}
        )

        # Count unique days with any health data this week
        health_dates = self._get_all_activity_dates()
        days_with_activity = len([
            d for d in health_dates
            if week_start <= d <= today
        ])

        progress.days_completed = days_with_activity
        progress.save()

    def _check_and_award_badges(self):
        """Check if user qualifies for new badges"""
        badges_to_check = [
            ('first_log', self._check_first_log),
            ('week_streak', self._check_week_streak),
            ('month_streak', self._check_month_streak),
            ('data_master', self._check_data_master),
            ('goal_achiever', self._check_goal_achiever),
            ('consistent', self._check_consistent),
        ]

        for badge_type, check_func in badges_to_check:
            if check_func():
                self._award_badge(badge_type)

    def _check_first_log(self):
        """Check if user has made their first log"""
        return self.streak.total_activities >= 1

    def _check_week_streak(self):
        """Check for 7-day streak"""
        return self.streak.current_streak >= 7

    def _check_month_streak(self):
        """Check for 30-day streak"""
        return self.streak.current_streak >= 30

    def _check_data_master(self):
        """Check for 100 total logs"""
        total_logs = (
                NutritionEntry.objects.filter(user=self.user).count() +
                ActivityData.objects.filter(user=self.user).count() +
                SleepData.objects.filter(user=self.user).count() +
                HealthMetrics.objects.filter(user=self.user).count()
        )
        return total_logs >= 100

    def _check_goal_achiever(self):
        """Check if user has completed any goals"""
        return Goal.objects.filter(user=self.user, status='completed').exists()

    def _check_consistent(self):
        """Check for longest streak of 14 days"""
        return self.streak.longest_streak >= 14

    def _award_badge(self, badge_type):
        """Award a badge to the user if they don't have it"""
        try:
            badge = Badge.objects.get(badge_type=badge_type)
            UserBadge.objects.get_or_create(user=self.user, badge=badge)
        except Badge.DoesNotExist:
            pass

    def _get_newly_earned_badges(self):
        """Get badges earned in the last minute"""
        one_minute_ago = timezone.now() - timedelta(minutes=1)
        return UserBadge.objects.filter(
            user=self.user,
            earned_at__gte=one_minute_ago
        )

    def get_user_stats(self):
        """Get all gamification stats for display"""
        today = timezone.localdate()
        week_start = today - timedelta(days=today.weekday())

        weekly_progress = WeeklyProgress.objects.filter(
            user=self.user,
            week_start=week_start
        ).first()

        return {
            'current_streak': self.streak.current_streak,
            'longest_streak': self.streak.longest_streak,
            'total_activities': self.streak.total_activities,
            'earned_badges': UserBadge.objects.filter(user=self.user),
            'weekly_progress': weekly_progress,
            'total_badges': Badge.objects.count(),
            'earned_badge_count': UserBadge.objects.filter(user=self.user).count(),
        }