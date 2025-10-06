from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone

# ----------------------------
# ORIGINAL MODELS (kept stable)
# ----------------------------

class NutritionEntry(models.Model):
    created_at = models.DateTimeField(default=timezone.now)
    calories = models.PositiveIntegerField(validators=[MinValueValidator(0)], default=0)
    protein_g = models.FloatField(validators=[MinValueValidator(0.0)], default=0.0)
    carbs_g = models.FloatField(validators=[MinValueValidator(0.0)], default=0.0)
    fat_g = models.FloatField(validators=[MinValueValidator(0.0)], default=0.0)
    description = models.CharField(max_length=255, blank=True, default="")

    def __str__(self):
        return f"Nutrition {self.created_at:%Y-%m-%d} - {self.calories} kcal"


class GlucoseEntry(models.Model):
    created_at = models.DateTimeField(default=timezone.now)
    glucose_mg_dl = models.FloatField(validators=[MinValueValidator(0.0)], default=0.0)

    def __str__(self):
        return f"Glucose {self.created_at:%Y-%m-%d} - {self.glucose_mg_dl} mg/dL"


class MedicationEntry(models.Model):
    created_at = models.DateTimeField(default=timezone.now)
    # Make these safe for existing rows (NO prompt):
    drug_name = models.CharField(max_length=120, default="Unknown", blank=True)
    dosage = models.CharField(max_length=120, blank=True, default="")
    time_taken = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Medication {self.created_at:%Y-%m-%d} - {self.drug_name or 'Unknown'}"


class DoctorNote(models.Model):
    created_at = models.DateTimeField(default=timezone.now)
    # Keep original field name "content" to avoid rename prompt:
    content = models.TextField(blank=True, default="")

    def __str__(self):
        return f"DoctorNote {self.created_at:%Y-%m-%d}"

# ----------------------------
# NEW MODELS (all safe defaults)
# ----------------------------

class ActivityLog(models.Model):
    created_at = models.DateTimeField(default=timezone.now)
    steps = models.PositiveIntegerField(default=0)
    distance_km = models.FloatField(validators=[MinValueValidator(0.0)], default=0.0)
    active_minutes = models.PositiveIntegerField(default=0)
    exercise_type = models.CharField(max_length=100, blank=True, default="")
    exercise_duration_min = models.PositiveIntegerField(default=0)
    floors = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"Activity {self.created_at:%Y-%m-%d} - {self.steps} steps"


class SleepLog(models.Model):
    created_at = models.DateTimeField(default=timezone.now)
    total_hours = models.FloatField(validators=[MinValueValidator(0.0)], default=0.0)
    quality = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)], default=3)
    bedtime = models.DateTimeField(default=timezone.now)
    wake_time = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Sleep {self.created_at:%Y-%m-%d} - {self.total_hours}h"


class VitalLog(models.Model):
    created_at = models.DateTimeField(default=timezone.now)
    resting_hr = models.PositiveIntegerField(default=0, help_text="beats per minute")
    systolic = models.PositiveIntegerField(default=0)
    diastolic = models.PositiveIntegerField(default=0)
    temperature_c = models.FloatField(validators=[MinValueValidator(30.0), MaxValueValidator(45.0)], default=36.5)

    def __str__(self):
        return f"Vitals {self.created_at:%Y-%m-%d} HR:{self.resting_hr}"


class MoodLog(models.Model):
    STRESS_CHOICES = [("low", "Low"), ("med", "Medium"), ("high", "High")]
    created_at = models.DateTimeField(default=timezone.now)
    mood_score = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(10)], default=5)
    stress_level = models.CharField(max_length=5, choices=STRESS_CHOICES, default="med")
    energy_level = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(10)], default=5)
    notes = models.TextField(blank=True, default="")

    def __str__(self):
        return f"Mood {self.created_at:%Y-%m-%d} mood:{self.mood_score}"


class SymptomLog(models.Model):
    created_at = models.DateTimeField(default=timezone.now)
    headache_intensity = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(10)], default=0)
    pain_location = models.CharField(max_length=100, blank=True, default="")
    pain_level = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(10)], default=0)
    digestion_notes = models.TextField(blank=True, default="")

    def __str__(self):
        return f"Symptoms {self.created_at:%Y-%m-%d} pain:{self.pain_level}"


class HabitLog(models.Model):
    created_at = models.DateTimeField(default=timezone.now)
    water_ml = models.PositiveIntegerField(default=0)
    caffeine_servings = models.PositiveIntegerField(default=0)
    alcohol_servings = models.PositiveIntegerField(default=0)
    medication_and_supplements = models.TextField(blank=True, default="")

    def __str__(self):
        return f"Habits {self.created_at:%Y-%m-%d} water:{self.water_ml}ml"


class WellbeingLog(models.Model):
    created_at = models.DateTimeField(default=timezone.now)
    mindfulness_minutes = models.PositiveIntegerField(default=0)
    time_outdoors_minutes = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"Well-being {self.created_at:%Y-%m-%d}"
