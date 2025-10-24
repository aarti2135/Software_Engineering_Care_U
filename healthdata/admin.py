from django.contrib import admin
from .models import NutritionEntry, HealthReminder, ActivityData, SleepData, HealthMetrics


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
