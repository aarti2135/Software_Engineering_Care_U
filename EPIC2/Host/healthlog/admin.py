from django.contrib import admin
from .models import (
    NutritionEntry, GlucoseEntry, MedicationEntry, DoctorNote,
    ActivityLog, SleepLog, VitalLog, MoodLog, SymptomLog, HabitLog, WellbeingLog
)

admin.site.register(NutritionEntry)
admin.site.register(GlucoseEntry)
admin.site.register(MedicationEntry)
admin.site.register(DoctorNote)

admin.site.register(ActivityLog)
admin.site.register(SleepLog)
admin.site.register(VitalLog)
admin.site.register(MoodLog)
admin.site.register(SymptomLog)
admin.site.register(HabitLog)
admin.site.register(WellbeingLog)
