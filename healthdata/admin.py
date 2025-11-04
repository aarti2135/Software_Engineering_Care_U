from django.contrib import admin
from .models import (
    NutritionEntry, HealthReminder, ActivityData, SleepData, HealthMetrics,
    GlucoseEntry, MedicationEntry, DoctorNote,
    VitalLog, MoodLog, SymptomLog, HabitLog, WellbeingLog
)


@admin.register(NutritionEntry)
class NutritionEntryAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'logged_at',
        'meal_type',
        'calories',
        'protein_g',
        'carbs_g',
        'fat_g',
    )
    list_filter = ('meal_type', 'logged_at', 'user')
    search_fields = ('user__username', 'notes')
    date_hierarchy = 'logged_at'


@admin.register(HealthReminder)
class HealthReminderAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'user',
        'reminder_type',
        'priority',
        'created_at',
        'is_active',
        'acted_upon'
    )
    list_filter = ('reminder_type', 'priority', 'acted_upon', 'created_at')
    search_fields = ('user__username', 'title', 'message')
    readonly_fields = ('created_at', 'acted_upon_at')

    fieldsets = (
        ('Basic Info', {
            'fields': ('user', 'reminder_type', 'priority', 'title')
        }),
        ('Content', {
            'fields': ('message', 'explanation', 'actionable_steps')
        }),
        ('Status', {
            'fields': ('created_at', 'dismissed_at', 'acted_upon', 'acted_upon_at')
        }),
    )

    def is_active(self, obj):
        return obj.is_active

    is_active.boolean = True
    is_active.short_description = 'Active'

@admin.register(ActivityData)
class ActivityDataAdmin(admin.ModelAdmin):
    list_display = ('user', 'date', 'activity_type', 'steps', 'active_minutes')
    list_filter = ('activity_type', 'date')
    search_fields = ('user__username',)

@admin.register(SleepData)
class SleepDataAdmin(admin.ModelAdmin):
    list_display = ('user', 'date', 'total_sleep_minutes', 'sleep_quality')
    list_filter = ('sleep_quality', 'date')
    search_fields = ('user__username',)

@admin.register(HealthMetrics)
class HealthMetricsAdmin(admin.ModelAdmin):
    list_display = ('user', 'logged_at', 'weight_kg', 'heart_rate_resting')
    list_filter = ('logged_at',)
    search_fields = ('user__username',)


# ---------------------------------------------------------------------
# Admin registrations for models migrated from healthlog
# ---------------------------------------------------------------------

@admin.register(GlucoseEntry)
class GlucoseEntryAdmin(admin.ModelAdmin):
    list_display = ('user', 'created_at', 'glucose_mg_dl')
    list_filter = ('created_at',)
    search_fields = ('user__username', 'notes')
    date_hierarchy = 'created_at'


@admin.register(MedicationEntry)
class MedicationEntryAdmin(admin.ModelAdmin):
    list_display = ('user', 'drug_name', 'dosage', 'time_taken', 'created_at')
    list_filter = ('time_taken', 'created_at')
    search_fields = ('user__username', 'drug_name', 'notes')
    date_hierarchy = 'time_taken'


@admin.register(DoctorNote)
class DoctorNoteAdmin(admin.ModelAdmin):
    list_display = ('user', 'doctor_name', 'appointment_date', 'created_at')
    list_filter = ('appointment_date', 'created_at')
    search_fields = ('user__username', 'doctor_name', 'content')
    date_hierarchy = 'created_at'


@admin.register(VitalLog)
class VitalLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'created_at', 'resting_hr', 'systolic', 'diastolic', 'temperature_c')
    list_filter = ('created_at',)
    search_fields = ('user__username', 'notes')
    date_hierarchy = 'created_at'


@admin.register(MoodLog)
class MoodLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'created_at', 'mood_score', 'stress_level', 'energy_level')
    list_filter = ('stress_level', 'created_at')
    search_fields = ('user__username', 'notes')
    date_hierarchy = 'created_at'


@admin.register(SymptomLog)
class SymptomLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'created_at', 'pain_level', 'headache_intensity', 'pain_location')
    list_filter = ('created_at',)
    search_fields = ('user__username', 'pain_location', 'digestion_notes', 'notes')
    date_hierarchy = 'created_at'


@admin.register(HabitLog)
class HabitLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'date', 'water_ml', 'caffeine_servings', 'alcohol_servings')
    list_filter = ('date',)
    search_fields = ('user__username', 'medication_and_supplements', 'notes')
    date_hierarchy = 'date'


@admin.register(WellbeingLog)
class WellbeingLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'date', 'mindfulness_minutes', 'time_outdoors_minutes')
    list_filter = ('date',)
    search_fields = ('user__username', 'notes')
    date_hierarchy = 'date'
