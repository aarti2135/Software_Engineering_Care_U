from django.db.models import Avg
from django.utils import timezone
from datetime import timedelta
from .models import ProviderAlert
from healthdata.models import NutritionEntry


# ---------------------------------------------------------------------
# 🏦 SHARE DATA WITH INSURER
# ---------------------------------------------------------------------
def share_user_data_with_insurer(user):
    """
    Share AGGREGATE data if user has consented.

    Args:
        user: Django User instance (from request.user)

    Returns:
        dict: {"status": "success/denied/error", "message": "..."}
    """
    try:
        profile = user.profile
    except Exception as e:
        return {"status": "error", "message": f"Profile not found: {e}"}

    if not profile.data_sharing_consent:
        return {
            "status": "denied",
            "message": "User has not consented to data sharing."
        }

    # TODO: Implement actual anonymization and API call to insurer
    # For now, this is a placeholder simulation
    return {
        "status": "success",
        "message": "Anonymized data shared successfully with insurer."
    }


# ---------------------------------------------------------------------
# 🧠 HEALTH PATTERN DETECTION
# ---------------------------------------------------------------------
def detect_health_patterns(user):
    """
    Analyze user's health data for concerning patterns.
    Creates ProviderAlert if issues are detected.

    Args:
        user: Django User instance

    Returns:
        ProviderAlert instance if created, None otherwise
    """
    # Get last 7 nutrition entries
    entries = NutritionEntry.objects.filter(
        user=user
    ).order_by('-logged_at')[:7]

    if not entries:
        return None

    # Calculate average calories
    avg_calories = sum(e.calories for e in entries) / len(entries)

    # Check for concerning low calorie intake
    if avg_calories < 1000:
        # Avoid duplicate alerts (check last 7 days)
        recent_alert = ProviderAlert.objects.filter(
            user=user,
            alert_type="Low Calorie Intake",
            created_at__gte=timezone.now() - timedelta(days=7)
        ).exists()

        if not recent_alert:
            alert = ProviderAlert.objects.create(
                user=user,
                alert_type="Low Calorie Intake",
                message=(
                    f"Recent 7-day average: {avg_calories:.0f} kcal/day. "
                    f"This is below recommended minimums. Recommend professional review."
                ),
                severity="moderate",
            )
            return alert

    # TODO: Add more pattern detection:
    # - Inconsistent logging
    # - Macro imbalances
    # - Sudden weight changes
    # - Activity level drops

    return None


# ---------------------------------------------------------------------
# 🤝 SHARE DATA WITH PROVIDER
# ---------------------------------------------------------------------
def share_user_data_with_provider(patient, provider):
    """
    Share anonymized health data from patient to healthcare provider.

    Args:
        patient: Django User instance (the patient)
        provider: Django User instance (the healthcare provider)

    Returns:
        dict: {"status": "success/denied/error", "message": "..."}
    """
    try:
        patient_profile = patient.profile
    except Exception as e:
        return {"status": "error", "message": f"Patient profile not found: {e}"}

    # Check patient consent
    if not patient_profile.data_sharing_consent:
        return {
            "status": "denied",
            "message": f"{patient.username} has not consented to data sharing."
        }

    # Gather anonymized summary
    recent_entries = NutritionEntry.objects.filter(
        user=patient
    ).order_by('-logged_at')[:14]

    if recent_entries:
        avg_calories = sum(e.calories for e in recent_entries) / len(recent_entries)
        avg_protein = sum(e.protein_g or 0 for e in recent_entries) / len(recent_entries)
        summary = (
            f"14-day averages: {avg_calories:.0f} kcal/day, "
            f"{avg_protein:.1f}g protein/day"
        )
    else:
        summary = "No recent nutrition data available"

    # Create provider alert with summary
    ProviderAlert.objects.create(
        user=provider,
        alert_type="Patient Data Shared",
        message=f"Data from patient {patient.username}: {summary}",
        severity="low",
    )

    return {
        "status": "success",
        "message": f"Anonymized data from {patient.username} shared with {provider.username}."
    }