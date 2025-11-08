# healthdata/urls.py
from django.urls import path, include
from rest_framework.routers import SimpleRouter
from .views import (
    NutritionEntryViewSet,
    HealthReminderViewSet,
    GlucoseEntryViewSet,
    MedicationEntryViewSet,
    DoctorNoteViewSet,
    VitalLogViewSet,
    MoodLogViewSet,
    SymptomLogViewSet,
    HabitLogViewSet,
    WellbeingLogViewSet,
    nutrition_dashboard,
    nutrition_edit,
    nutrition_delete,
    reminders_dashboard,
    dismiss_reminder,
    act_on_reminder,
)

router = SimpleRouter()
router.register('nutrition', NutritionEntryViewSet, basename='nutrition')
router.register('reminders', HealthReminderViewSet, basename='reminders')
router.register('glucose', GlucoseEntryViewSet, basename='glucose')
router.register('medication', MedicationEntryViewSet, basename='medication')
router.register('doctornotes', DoctorNoteViewSet, basename='doctornotes')
router.register('vitals', VitalLogViewSet, basename='vitals')
router.register('mood', MoodLogViewSet, basename='mood')
router.register('symptoms', SymptomLogViewSet, basename='symptoms')
router.register('habits', HabitLogViewSet, basename='habits')
router.register('wellbeing', WellbeingLogViewSet, basename='wellbeing')


urlpatterns = [
    path('', include(router.urls)),

    # Nutrition HTML views
    path('dashboard/nutrition/', nutrition_dashboard, name='nutrition_dashboard'),
    path('dashboard/nutrition/<int:pk>/edit/', nutrition_edit, name='nutrition_edit'),
    path('dashboard/nutrition/<int:pk>/delete/', nutrition_delete, name='nutrition_delete'),

    # Reminders HTML views
    path('dashboard/reminders/', reminders_dashboard, name='reminders_dashboard'),
    path('dashboard/reminders/<int:pk>/dismiss/', dismiss_reminder, name='dismiss_reminder'),
    path('dashboard/reminders/<int:pk>/act/', act_on_reminder, name='act_on_reminder'),
]

