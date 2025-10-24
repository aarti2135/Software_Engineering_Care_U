from django.conf import settings
from django.db import models
from django.utils import timezone

class NutritionEntry(models.Model):
    MEAL_CHOICES = [
        ("breakfast", "Breakfast"),
        ("lunch", "Lunch"),
        ("dinner", "Dinner"),
        ("snack", "Snack"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="nutrition_entries",
    )
    logged_at = models.DateField(default=timezone.now)
    meal_type = models.CharField(max_length=16, choices=MEAL_CHOICES)
    calories = models.PositiveIntegerField()
    protein_g = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    carbs_g = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    fat_g = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-logged_at", "-created_at"]

    def __str__(self):
        return f"{self.user} {self.meal_type} on {self.logged_at} ({self.calories} kcal)"

class HealthReminder(models.Model):
    """
    Stores personalized health reminders for users.
    Provides clear explanations to build trust.
    """
    REMINDER_TYPES = [
        ('nutrition', 'Nutrition'),
        ('activity', 'Activity'),
        ('hydration', 'Hydration'),
        ('sleep', 'Sleep'),
        ('general', 'General'),
    ]

    PRIORITY_LEVELS = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='health_reminders'
    )
    reminder_type = models.CharField(max_length=20, choices=REMINDER_TYPES)
    title = models.CharField(max_length=200)
    message = models.TextField(help_text="Short message (1-2 sentences)")
    explanation = models.TextField(help_text="Detailed explanation of WHY this matters")
    priority = models.CharField(max_length=10, choices=PRIORITY_LEVELS, default='medium')
    actionable_steps = models.JSONField(
        default=list,
        help_text="List of specific actions user can take"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    dismissed_at = models.DateTimeField(null=True, blank=True)
    acted_upon = models.BooleanField(default=False)
    acted_upon_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'dismissed_at']),
        ]

    def __str__(self):
        return f"{self.title} ({self.user.username})"

    @property
    def is_active(self):
        """Check if reminder is still active (not dismissed)"""
        return self.dismissed_at is None

class ActivityData(models.Model):
    """
    Stores activity data from wearables (steps, distance, active minutes).
    """
    ACTIVITY_TYPES = [
        ('walking', 'Walking'),
        ('running', 'Running'),
        ('cycling', 'Cycling'),
        ('swimming', 'Swimming'),
        ('workout', 'Workout'),
        ('general', 'General'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='activity_data'
    )
    date = models.DateField(default=timezone.now)
    activity_type = models.CharField(max_length=20, choices=ACTIVITY_TYPES, default='general')

    # Core metrics
    steps = models.PositiveIntegerField(default=0)
    distance_km = models.DecimalField(max_digits=6, decimal_places=2, default=0)  # kilometers
    active_minutes = models.PositiveIntegerField(default=0)  # minutes of moderate+ activity
    calories_burned = models.PositiveIntegerField(default=0)

    # Additional metrics
    heart_rate_avg = models.PositiveIntegerField(null=True, blank=True)  # average BPM
    heart_rate_max = models.PositiveIntegerField(null=True, blank=True)  # max BPM
    floors_climbed = models.PositiveIntegerField(default=0)  # floors or elevation gain

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date', '-created_at']
        unique_together = ['user', 'date', 'activity_type']

    def __str__(self):
        return f"{self.user} - {self.date} - {self.steps} steps"

class SleepData(models.Model):
    """
    Stores sleep data from wearables.
    """
    SLEEP_QUALITY = [
        ('poor', 'Poor'),
        ('fair', 'Fair'),
        ('good', 'Good'),
        ('excellent', 'Excellent'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='sleep_data'
    )
    date = models.DateField(default=timezone.now)

    # Sleep duration
    total_sleep_minutes = models.PositiveIntegerField()  # total time in bed
    deep_sleep_minutes = models.PositiveIntegerField(null=True, blank=True)
    light_sleep_minutes = models.PositiveIntegerField(null=True, blank=True)
    rem_sleep_minutes = models.PositiveIntegerField(null=True, blank=True)
    awake_minutes = models.PositiveIntegerField(null=True, blank=True)

    # Sleep quality metrics
    sleep_quality = models.CharField(max_length=10, choices=SLEEP_QUALITY, null=True, blank=True)
    sleep_score = models.PositiveIntegerField(null=True, blank=True)  # 0-100 score
    times_awake = models.PositiveIntegerField(default=0)  # number of awakenings

    # Timestamps
    bedtime_start = models.DateTimeField(null=True, blank=True)
    bedtime_end = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date']
        unique_together = ['user', 'date']

    def __str__(self):
        return f"{self.user} - {self.date} - {self.total_sleep_minutes} min sleep"

class HealthMetrics(models.Model):
    """
    Stores periodic health metrics (weight, heart rate, blood pressure, etc.).
    Can be manual entry or from wearables.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='health_metrics'
    )
    logged_at = models.DateTimeField(default=timezone.now)

    # Vital signs
    weight_kg = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    heart_rate_resting = models.PositiveIntegerField(null=True, blank=True)  # resting heart rate
    blood_pressure_systolic = models.PositiveIntegerField(null=True, blank=True)
    blood_pressure_diastolic = models.PositiveIntegerField(null=True, blank=True)
    blood_oxygen = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True)  # SpO2 %

    # Body composition (if available)
    body_fat_percentage = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True)
    muscle_mass_kg = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)

    # Additional metrics
    stress_level = models.PositiveIntegerField(null=True, blank=True, help_text="0-100 scale")  # 0-100 scale
    hrv = models.PositiveIntegerField(null=True, blank=True,
                                      help_text="Heart Rate Variability")  # Heart Rate Variability

    notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-logged_at']

    def __str__(self):
        return f"{self.user} - {self.logged_at.date()} - Health Metrics"