from rest_framework import serializers
from .models import (
    NutritionEntry, HealthReminder,
    GlucoseEntry, MedicationEntry, DoctorNote,
    VitalLog, MoodLog, SymptomLog, HabitLog, WellbeingLog
)

class NutritionEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = NutritionEntry
        fields = [
            "id", "logged_at", "meal_type", "calories",
            "protein_g", "carbs_g", "fat_g", "notes",
            "created_at", "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate(self, attrs):
        for f in ["protein_g", "carbs_g", "fat_g"]:
            v = attrs.get(f)
            if v is not None and v < 0:
                raise serializers.ValidationError({f: "Cannot be negative."})
        if attrs.get("calories", 0) < 0:
            raise serializers.ValidationError({"calories": "Cannot be negative."})
        return attrs


class HealthReminderSerializer(serializers.ModelSerializer):
    """
    Serializer for HealthReminder API.
    Provides read-only access to reminders and actions to dismiss/act on them.
    """
    is_active = serializers.ReadOnlyField()

    class Meta:
        model = HealthReminder
        fields = [
            'id',
            'reminder_type',
            'title',
            'message',
            'explanation',
            'priority',
            'actionable_steps',
            'created_at',
            'dismissed_at',
            'acted_upon',
            'acted_upon_at',
            'is_active',
        ]
        read_only_fields = [
            'id',
            'created_at',
            'dismissed_at',
            'acted_upon_at',
        ]


# ---------------------------------------------------------------------
# Serializers for models migrated from healthlog
# ---------------------------------------------------------------------

class GlucoseEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = GlucoseEntry
        fields = [
            'id', 'user', 'created_at', 'glucose_mg_dl', 'notes'
        ]
        read_only_fields = ['id', 'user', 'created_at']

    def validate_glucose_mg_dl(self, value):
        if value < 0:
            raise serializers.ValidationError("Glucose level cannot be negative.")
        return value


class MedicationEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = MedicationEntry
        fields = [
            'id', 'user', 'created_at', 'drug_name', 'dosage',
            'time_taken', 'notes'
        ]
        read_only_fields = ['id', 'user', 'created_at']


class DoctorNoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = DoctorNote
        fields = [
            'id', 'user', 'created_at', 'content', 'doctor_name', 'appointment_date'
        ]
        read_only_fields = ['id', 'user', 'created_at']


class VitalLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = VitalLog
        fields = [
            'id', 'user', 'created_at', 'resting_hr', 'systolic',
            'diastolic', 'temperature_c', 'notes'
        ]
        read_only_fields = ['id', 'user', 'created_at']

    def validate_temperature_c(self, value):
        if value < 30.0 or value > 45.0:
            raise serializers.ValidationError("Temperature must be between 30.0 and 45.0 Celsius.")
        return value


class MoodLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = MoodLog
        fields = [
            'id', 'user', 'created_at', 'mood_score', 'stress_level',
            'energy_level', 'notes'
        ]
        read_only_fields = ['id', 'user', 'created_at']

    def validate_mood_score(self, value):
        if value < 1 or value > 10:
            raise serializers.ValidationError("Mood score must be between 1 and 10.")
        return value

    def validate_energy_level(self, value):
        if value < 1 or value > 10:
            raise serializers.ValidationError("Energy level must be between 1 and 10.")
        return value


class SymptomLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = SymptomLog
        fields = [
            'id', 'user', 'created_at', 'headache_intensity', 'pain_location',
            'pain_level', 'digestion_notes', 'notes'
        ]
        read_only_fields = ['id', 'user', 'created_at']

    def validate_headache_intensity(self, value):
        if value < 0 or value > 10:
            raise serializers.ValidationError("Headache intensity must be between 0 and 10.")
        return value

    def validate_pain_level(self, value):
        if value < 0 or value > 10:
            raise serializers.ValidationError("Pain level must be between 0 and 10.")
        return value


class HabitLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = HabitLog
        fields = [
            'id', 'user', 'created_at', 'date', 'water_ml',
            'caffeine_servings', 'alcohol_servings', 'medication_and_supplements', 'notes'
        ]
        read_only_fields = ['id', 'user', 'created_at']


class WellbeingLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = WellbeingLog
        fields = [
            'id', 'user', 'created_at', 'date', 'mindfulness_minutes',
            'time_outdoors_minutes', 'notes'
        ]
        read_only_fields = ['id', 'user', 'created_at']
