from rest_framework import serializers
from .models import (
    # existing
    NutritionEntry, GlucoseEntry, MedicationEntry, DoctorNote,
    # new
    ActivityLog, SleepLog, VitalLog, MoodLog, SymptomLog, HabitLog, WellbeingLog
)

# ----- existing serializers (keep yours) -----
class NutritionEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = NutritionEntry
        fields = "__all__"

class GlucoseEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = GlucoseEntry
        fields = "__all__"

class MedicationEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = MedicationEntry
        fields = "__all__"

class DoctorNoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = DoctorNote
        fields = "__all__"

# ----- new serializers -----
class ActivityLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = ActivityLog
        fields = "__all__"

class SleepLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = SleepLog
        fields = "__all__"

class VitalLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = VitalLog
        fields = "__all__"

class MoodLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = MoodLog
        fields = "__all__"

class SymptomLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = SymptomLog
        fields = "__all__"

class HabitLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = HabitLog
        fields = "__all__"

class WellbeingLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = WellbeingLog
        fields = "__all__"
