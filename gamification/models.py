from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Badge(models.Model):
    """Available badges in the system"""
    BADGE_TYPES = [
        ('first_log', 'First Log'),
        ('week_streak', '7-Day Streak'),
        ('month_streak', '30-Day Streak'),
        ('data_master', 'Data Master (100 logs)'),
        ('goal_achiever', 'Goal Achiever'),
        ('consistent', 'Consistency Champion'),
    ]

    name = models.CharField(max_length=100)
    badge_type = models.CharField(max_length=50, choices=BADGE_TYPES, unique=True)
    description = models.TextField()
    icon = models.CharField(max_length=10, default='🏆')  # Emoji icon
    requirement = models.IntegerField(default=1)  # Number needed to earn

    def __str__(self):
        return self.name


class UserBadge(models.Model):
    """Badges earned by users"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='earned_badges')
    badge = models.ForeignKey(Badge, on_delete=models.CASCADE)
    earned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'badge')
        ordering = ['-earned_at']

    def __str__(self):
        return f"{self.user.username} - {self.badge.name}"


class UserStreak(models.Model):
    """Track user login/activity streaks"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='streak')
    current_streak = models.IntegerField(default=0)
    longest_streak = models.IntegerField(default=0)
    last_activity_date = models.DateField(null=True, blank=True)
    total_activities = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.user.username} - {self.current_streak} day streak"

    def update_streak(self):
        """Update streak based on today's activity"""
        today = timezone.localdate()

        if self.last_activity_date is None:
            # First activity ever
            self.current_streak = 1
            self.longest_streak = 1
            self.last_activity_date = today
            self.total_activities = 1
        elif self.last_activity_date == today:
            # Already logged today, no change
            pass
        elif self.last_activity_date == today - timezone.timedelta(days=1):
            # Consecutive day - increment streak
            self.current_streak += 1
            self.longest_streak = max(self.longest_streak, self.current_streak)
            self.last_activity_date = today
            self.total_activities += 1
        else:
            # Streak broken - reset
            self.current_streak = 1
            self.last_activity_date = today
            self.total_activities += 1

        self.save()
        return self.current_streak


class WeeklyProgress(models.Model):
    """Track weekly engagement goals"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='weekly_progress')
    week_start = models.DateField()
    goal_target = models.IntegerField(default=7)  # Days per week goal
    days_completed = models.IntegerField(default=0)

    class Meta:
        unique_together = ('user', 'week_start')
        ordering = ['-week_start']

    def __str__(self):
        return f"{self.user.username} - Week of {self.week_start}"

    @property
    def progress_percentage(self):
        return int((self.days_completed / self.goal_target) * 100)

    @property
    def is_complete(self):
        return self.days_completed >= self.goal_target