from django.conf import settings
from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator

# ---------------------------------------------------------------------
# Core Models
# ---------------------------------------------------------------------

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
    """Stores personalized health reminders for users."""
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
    actionable_steps = models.JSONField(default=list, help_text="List of specific actions user can take")

    created_at = models.DateTimeField(auto_now_add=True)
    dismissed_at = models.DateTimeField(null=True, blank=True)
    acted_upon = models.BooleanField(default=False)
    acted_upon_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [models.Index(fields=['user', 'dismissed_at'])]

    def __str__(self):
        return f"{self.title} ({self.user.username})"

    @property
    def is_active(self):
        return self.dismissed_at is None


# ---------------------------------------------------------------------
# Activity / Sleep / Metrics Models
# ---------------------------------------------------------------------

class ActivityData(models.Model):
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
    steps = models.PositiveIntegerField(default=0)
    distance_km = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    active_minutes = models.PositiveIntegerField(default=0)
    calories_burned = models.PositiveIntegerField(default=0)
    heart_rate_avg = models.PositiveIntegerField(null=True, blank=True)
    heart_rate_max = models.PositiveIntegerField(null=True, blank=True)
    floors_climbed = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date', '-created_at']
        unique_together = ['user', 'date', 'activity_type']

    def __str__(self):
        return f"{self.user} - {self.date} - {self.steps} steps"


class SleepData(models.Model):
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
    total_sleep_minutes = models.PositiveIntegerField()
    deep_sleep_minutes = models.PositiveIntegerField(null=True, blank=True)
    light_sleep_minutes = models.PositiveIntegerField(null=True, blank=True)
    rem_sleep_minutes = models.PositiveIntegerField(null=True, blank=True)
    awake_minutes = models.PositiveIntegerField(null=True, blank=True)
    sleep_quality = models.CharField(max_length=10, choices=SLEEP_QUALITY, null=True, blank=True)
    sleep_score = models.PositiveIntegerField(null=True, blank=True)
    times_awake = models.PositiveIntegerField(default=0)
    bedtime_start = models.DateTimeField(null=True, blank=True)
    bedtime_end = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date']
        unique_together = ['user', 'date']

    def __str__(self):
        return f"{self.user} - {self.date} - {self.total_sleep_minutes} min sleep"


class HealthMetrics(models.Model):
    """Stores periodic health metrics (weight, heart rate, BP, etc.)."""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='health_metrics'
    )
    logged_at = models.DateTimeField(default=timezone.now)
    weight_kg = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    heart_rate_resting = models.PositiveIntegerField(null=True, blank=True)
    blood_pressure_systolic = models.PositiveIntegerField(null=True, blank=True)
    blood_pressure_diastolic = models.PositiveIntegerField(null=True, blank=True)
    blood_oxygen = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True)
    body_fat_percentage = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True)
    muscle_mass_kg = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    stress_level = models.PositiveIntegerField(null=True, blank=True, help_text="0-100 scale")
    hrv = models.PositiveIntegerField(null=True, blank=True, help_text="Heart Rate Variability")
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-logged_at']

    def __str__(self):
        return f"{self.user} - {self.logged_at.date()} - Health Metrics"


# ---------------------------------------------------------------------
# Health Log Models (glucose, meds, vitals, mood, etc.)
# ---------------------------------------------------------------------

class GlucoseEntry(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='glucose_entries')
    created_at = models.DateTimeField(default=timezone.now)
    glucose_mg_dl = models.FloatField(validators=[MinValueValidator(0.0)], help_text="Glucose level in mg/dL")
    notes = models.TextField(blank=True, default="")
    class Meta: ordering = ['-created_at']
    def __str__(self): return f"{self.user} - {self.created_at:%Y-%m-%d} - {self.glucose_mg_dl} mg/dL"


class MedicationEntry(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='medication_entries')
    created_at = models.DateTimeField(default=timezone.now)
    drug_name = models.CharField(max_length=120, default="Unknown")
    dosage = models.CharField(max_length=120, blank=True, default="")
    time_taken = models.DateTimeField(default=timezone.now)
    notes = models.TextField(blank=True, default="")
    class Meta: ordering = ['-time_taken', '-created_at']
    def __str__(self): return f"{self.user} - {self.created_at:%Y-%m-%d} - {self.drug_name or 'Unknown'}"


class DoctorNote(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='doctor_notes')
    created_at = models.DateTimeField(default=timezone.now)
    content = models.TextField(help_text="Doctor's notes or medical information")
    doctor_name = models.CharField(max_length=200, blank=True, default="")
    appointment_date = models.DateField(null=True, blank=True)
    class Meta: ordering = ['-created_at']
    def __str__(self): return f"{self.user} - DoctorNote {self.created_at:%Y-%m-%d}"


class VitalLog(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='vital_logs')
    created_at = models.DateTimeField(default=timezone.now)
    resting_hr = models.PositiveIntegerField(default=0, help_text="Resting heart rate (BPM)")
    systolic = models.PositiveIntegerField(default=0, help_text="Systolic BP")
    diastolic = models.PositiveIntegerField(default=0, help_text="Diastolic BP")
    temperature_c = models.FloatField(validators=[MinValueValidator(30.0), MaxValueValidator(45.0)], default=36.5)
    notes = models.TextField(blank=True, default="")
    class Meta: ordering = ['-created_at']
    def __str__(self): return f"{self.user} - {self.created_at:%Y-%m-%d} HR:{self.resting_hr} BP:{self.systolic}/{self.diastolic}"


class MoodLog(models.Model):
    STRESS_CHOICES = [("low", "Low"), ("med", "Medium"), ("high", "High")]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='mood_logs')
    created_at = models.DateTimeField(default=timezone.now)
    mood_score = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(10)], default=5)
    stress_level = models.CharField(max_length=5, choices=STRESS_CHOICES, default="med")
    energy_level = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(10)], default=5)
    notes = models.TextField(blank=True, default="")
    class Meta: ordering = ['-created_at']
    def __str__(self): return f"{self.user} - {self.created_at:%Y-%m-%d} mood:{self.mood_score} stress:{self.stress_level}"


class SymptomLog(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='symptom_logs')
    created_at = models.DateTimeField(default=timezone.now)
    headache_intensity = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(10)], default=0)
    pain_location = models.CharField(max_length=100, blank=True, default="")
    pain_level = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(10)], default=0)
    digestion_notes = models.TextField(blank=True, default="")
    notes = models.TextField(blank=True, default="")
    class Meta: ordering = ['-created_at']
    def __str__(self): return f"{self.user} - {self.created_at:%Y-%m-%d} pain:{self.pain_level}"


class HabitLog(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='habit_logs')
    created_at = models.DateTimeField(default=timezone.now)
    date = models.DateField(default=timezone.now)
    water_ml = models.PositiveIntegerField(default=0)
    caffeine_servings = models.PositiveIntegerField(default=0)
    alcohol_servings = models.PositiveIntegerField(default=0)
    medication_and_supplements = models.TextField(blank=True, default="")
    notes = models.TextField(blank=True, default="")
    class Meta:
        ordering = ['-date', '-created_at']
        unique_together = ['user', 'date']
    def __str__(self): return f"{self.user} - {self.date} - water:{self.water_ml}ml"


class WellbeingLog(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='wellbeing_logs')
    created_at = models.DateTimeField(default=timezone.now)
    date = models.DateField(default=timezone.now)
    mindfulness_minutes = models.PositiveIntegerField(default=0)
    time_outdoors_minutes = models.PositiveIntegerField(default=0)
    notes = models.TextField(blank=True, default="")
    class Meta:
        ordering = ['-date', '-created_at']
        unique_together = ['user', 'date']
    def __str__(self): return f"{self.user} - {self.date} - mindfulness:{self.mindfulness_minutes} outdoor:{self.time_outdoors_minutes}"


# ---------------------------------------------------------------------
# Goal + Progress Models (Enhanced)
# ---------------------------------------------------------------------

class Goal(models.Model):
    """User-defined health goals (steps, calories, hydration, etc.) with auto-progress tracking."""
    class GoalType(models.TextChoices):
        STEPS = "steps", "Steps"
        DISTANCE_KM = "distance_km", "Distance (km)"
        ACTIVE_MIN = "active_min", "Active minutes"
        CALORIES = "calories", "Calories burned"
        WEIGHT = "weight", "Weight"
        WATER_L = "water_l", "Water (L)"
        PROTEIN_G = "protein_g", "Protein (g)"
        CARBS_G = "carbs_g", "Carbs (g)"
        FAT_G = "fat_g", "Fat (g)"

    class Frequency(models.TextChoices):
        DAILY = "daily", "Daily"
        WEEKLY = "weekly", "Weekly"
        MONTHLY = "monthly", "Monthly"
        ONE_OFF = "one_off", "One-off"

    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        PAUSED = "paused", "Paused"
        COMPLETED = "completed", "Completed"
        EXPIRED = "expired", "Expired"

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="goals")
    goal_type = models.CharField(max_length=32, choices=GoalType.choices)
    frequency = models.CharField(max_length=16, choices=Frequency.choices, default=Frequency.DAILY)
    target_value = models.FloatField(validators=[MinValueValidator(0.0)])
    current_value = models.FloatField(default=0.0, validators=[MinValueValidator(0.0)])
    progress = models.FloatField(default=0.0, help_text="Percentage of progress toward goal")  # ✅ Added field
    start_date = models.DateField(default=timezone.localdate)
    due_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.ACTIVE)
    title = models.CharField(max_length=120, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return self.title or f"{self.get_goal_type_display()} → {self.target_value}"

    def update_progress(self, value):
        """Update both numeric progress and status automatically."""
        self.current_value = min(value, self.target_value)
        if self.target_value > 0:
            self.progress = min(round((self.current_value / self.target_value) * 100, 1), 100)
        if self.progress >= 100:
            self.status = self.Status.COMPLETED
        self.save(update_fields=["current_value", "progress", "status", "updated_at"])


class GoalProgressLog(models.Model):
    """Tracks incremental updates toward a goal for analytics."""
    goal = models.ForeignKey(Goal, on_delete=models.CASCADE, related_name="logs")
    applied_on = models.DateField(default=timezone.localdate)
    delta_value = models.FloatField(validators=[MinValueValidator(0.0)])
    source = models.CharField(max_length=64, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-created_at",)
        indexes = [models.Index(fields=["applied_on"])]

    def __str__(self):
        return f"+{self.delta_value} on {self.applied_on} ({self.source or 'n/a'})"
