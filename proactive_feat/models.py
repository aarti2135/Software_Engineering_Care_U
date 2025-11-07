from django.conf import settings
from django.db import models
from django.utils import timezone

User = settings.AUTH_USER_MODEL

class VitalReading(models.Model):
    VITAL_CHOICES = [
        ("glucose", "Glucose (mg/dL)"),
        ("bp_sys",  "BP Systolic"),
        ("bp_dia",  "BP Diastolic"),
        ("hr",      "Heart Rate (bpm)"),
        ("spo2",    "SpO2 (%)"),
        ("temp",    "Body Temp (°C)"),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    kind = models.CharField(max_length=16, choices=VITAL_CHOICES)
    value = models.FloatField()
    measured_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["-measured_at"]

class MedicationLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=120)
    dosage = models.CharField(max_length=60, blank=True)
    taken_at = models.DateTimeField(default=timezone.now)

class DoctorNote(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Alert(models.Model):
    ALERT_TYPES = [
        ("threshold", "Abnormal vital detected"),
        ("missed_log", "Missed log/reminder"),
        ("trend",     "Repeated abnormal pattern"),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="alerts")
    alert_type = models.CharField(max_length=16, choices=ALERT_TYPES)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    is_dismissed = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_at"]
