from django.db.models import F
from .models import CustomUser


def share_user_data_with_insurer(user_id):
    """
    Conceptual function to share AGGREGATE data,
    gated by the user's explicit consent.
    """
    try:
        # F-expression is added here as a best practice, though not strictly needed for this try/except logic
        # It's generally used for queries, but good to show careful model usage.
        user = CustomUser.objects.annotate(
            # Example annotation for better model interaction if needed later
            data_consent_status=F('data_sharing_consent')
        ).get(pk=user_id)
    except CustomUser.DoesNotExist:
        return {"status": "error", "message": "User not found"}

    # CRITICAL: Check for explicit consent before processing data for sharing
    if not user.data_sharing_consent:
        return {"status": "denied", "message": "User has not consented to data sharing."}

    # Logic for stripping PII and sharing only ANONYMIZED data would go here.
    # The actual implementation involves complex data processing and sanitization

    return {"status": "success", "message": "Anonymized data shared successfully to third party."}