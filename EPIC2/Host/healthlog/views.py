from rest_framework import viewsets, permissions
from .models import (
    NutritionEntry, GlucoseEntry, MedicationEntry, DoctorNote,
    ActivityLog, SleepLog, VitalLog, MoodLog, SymptomLog, HabitLog, WellbeingLog
)
from .serializers import (
    NutritionEntrySerializer, GlucoseEntrySerializer, MedicationEntrySerializer, DoctorNoteSerializer,
    ActivityLogSerializer, SleepLogSerializer, VitalLogSerializer, MoodLogSerializer,
    SymptomLogSerializer, HabitLogSerializer, WellbeingLogSerializer
)

# existing viewsets
class NutritionEntryViewSet(viewsets.ModelViewSet):
    queryset = NutritionEntry.objects.all().order_by("-id")
    serializer_class = NutritionEntrySerializer
    permission_classes = [permissions.AllowAny]

class GlucoseEntryViewSet(viewsets.ModelViewSet):
    queryset = GlucoseEntry.objects.all().order_by("-id")
    serializer_class = GlucoseEntrySerializer
    permission_classes = [permissions.AllowAny]

class MedicationEntryViewSet(viewsets.ModelViewSet):
    queryset = MedicationEntry.objects.all().order_by("-id")
    serializer_class = MedicationEntrySerializer
    permission_classes = [permissions.AllowAny]

class DoctorNoteViewSet(viewsets.ModelViewSet):
    queryset = DoctorNote.objects.all().order_by("-id")
    serializer_class = DoctorNoteSerializer
    permission_classes = [permissions.AllowAny]

# new viewsets
class ActivityLogViewSet(viewsets.ModelViewSet):
    queryset = ActivityLog.objects.all().order_by("-id")
    serializer_class = ActivityLogSerializer
    permission_classes = [permissions.AllowAny]

class SleepLogViewSet(viewsets.ModelViewSet):
    queryset = SleepLog.objects.all().order_by("-id")
    serializer_class = SleepLogSerializer
    permission_classes = [permissions.AllowAny]

class VitalLogViewSet(viewsets.ModelViewSet):
    queryset = VitalLog.objects.all().order_by("-id")
    serializer_class = VitalLogSerializer
    permission_classes = [permissions.AllowAny]

class MoodLogViewSet(viewsets.ModelViewSet):
    queryset = MoodLog.objects.all().order_by("-id")
    serializer_class = MoodLogSerializer
    permission_classes = [permissions.AllowAny]

class SymptomLogViewSet(viewsets.ModelViewSet):
    queryset = SymptomLog.objects.all().order_by("-id")
    serializer_class = SymptomLogSerializer
    permission_classes = [permissions.AllowAny]

class HabitLogViewSet(viewsets.ModelViewSet):
    queryset = HabitLog.objects.all().order_by("-id")
    serializer_class = HabitLogSerializer
    permission_classes = [permissions.AllowAny]

class WellbeingLogViewSet(viewsets.ModelViewSet):
    queryset = WellbeingLog.objects.all().order_by("-id")
    serializer_class = WellbeingLogSerializer
    permission_classes = [permissions.AllowAny]
