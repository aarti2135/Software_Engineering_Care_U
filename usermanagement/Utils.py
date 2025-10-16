from django.db.models import F
from .models import CustomUser, ProviderAlert
from healthdata.models import NutritionEntry


# ---------------------------------------------------------------------
# 🏦 SHARE DATA WITH INSURER (existing function)
# ---------------------------------------------------------------------
def share_user_data_with_insurer(user_id):
    """
    Conceptual function to share AGGREGATE data,
    gated by the user's explicit consent.
    """
    try:
        user = CustomUser.objects.annotate(
            data_consent_status=F('data_sharing_consent')
        ).get(pk=user_id)
    except CustomUser.DoesNotExist:
        return {"status": "error", "message": "User not found"}

    if not user.data_sharing_consent:
        return {"status": "denied", "message": "User has not consented to data sharing."}

    # Logic for anonymization (placeholder)
    return {"status": "success", "message": "Anonymized data shared successfully to third party."}


# ---------------------------------------------------------------------
# 🧠 HEALTH PATTERN DETECTION FOR PROVIDER ALERTS
# ---------------------------------------------------------------------
def detect_health_patterns(user):
    """
    Simple placeholder for AI or trend detection logic.
    Currently checks for suspicious calorie patterns
    as an example of 'concerning change detection'.
    """
    entries = NutritionEntry.objects.filter(user=user).order_by('-logged_at')[:7]
    if not entries:
        return None

    avg_calories = sum(e.calories for e in entries) / len(entries)
    if avg_calories < 1000:  # Example threshold for demo
        alert = ProviderAlert.objects.create(
            user=user,
            alert_type="Low Calorie Intake",
            message="User's recent calorie intake has been consistently low. Recommend professional review.",
            severity="moderate",
        )
        return alert

    return None


# ---------------------------------------------------------------------
# 🤝 SHARE DATA WITH PROVIDER (NEW FUNCTION)
# ---------------------------------------------------------------------
def share_user_data_with_provider(patient_id, provider_id):
    """
    Simulates sharing anonymized health data between two users
    (patient → provider), verifying consent before proceeding.
    """
    try:
        patient = CustomUser.objects.get(pk=patient_id)
        provider = CustomUser.objects.get(pk=provider_id)
    except CustomUser.DoesNotExist:
        return {"status": "error", "message": "Patient or provider not found."}

    # Check patient's consent
    if not patient.data_sharing_consent:
        return {"status": "denied", "message": f"{patient.username} has not consented to data sharing."}

    # Simulate anonymization and provider alert creation
    ProviderAlert.objects.create(
        user=provider,
        alert_type="Shared Data Received",
        message=f"Anonymized health data received from {patient.username}.",
        severity="low",
    )

    return {"status": "success", "message": f"Anonymized data from {patient.username} shared with {provider.username}."}
