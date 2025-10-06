from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    NutritionEntryViewSet, GlucoseEntryViewSet, MedicationEntryViewSet, DoctorNoteViewSet,
    ActivityLogViewSet, SleepLogViewSet, VitalLogViewSet, MoodLogViewSet,
    SymptomLogViewSet, HabitLogViewSet, WellbeingLogViewSet
)

router = DefaultRouter()
# existing
router.register(r"nutrition", NutritionEntryViewSet, basename="nutrition")
router.register(r"glucose", GlucoseEntryViewSet, basename="glucose")
router.register(r"medication", MedicationEntryViewSet, basename="medication")
router.register(r"doctornotes", DoctorNoteViewSet, basename="doctornotes")
# new
router.register(r"activity", ActivityLogViewSet, basename="activity")
router.register(r"sleep", SleepLogViewSet, basename="sleep")
router.register(r"vitals", VitalLogViewSet, basename="vitals")
router.register(r"mood", MoodLogViewSet, basename="mood")
router.register(r"symptoms", SymptomLogViewSet, basename="symptoms")
router.register(r"habits", HabitLogViewSet, basename="habits")
router.register(r"wellbeing", WellbeingLogViewSet, basename="wellbeing")

urlpatterns = [
    path("", include(router.urls)),
]
