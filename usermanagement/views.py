# usermanagement/views.py

from django.shortcuts import render, redirect
from django.views import View
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import get_user_model
from django.utils import timezone

from usermanagement.utils import (
    share_user_data_with_insurer,
    share_user_data_with_provider,
)
from usermanagement.models import Profile, ProviderAlert

User = get_user_model()


# ======================================================================
# CONSENT MANAGEMENT
# ======================================================================

class ConsentView(LoginRequiredMixin, View):
    """Handle user consent for data sharing."""
    template_name = "usermanagement/consent.html"

    def get(self, request):
        """Render the consent page showing current status."""
        profile, _ = Profile.objects.get_or_create(user=request.user)

        context = {
            "current_consent": profile.data_sharing_consent,
            "consent_date": profile.consent_timestamp,
        }
        return render(request, self.template_name, context)

    def post(self, request):
        """Handle form submission (Yes / No consent)."""
        user = request.user
        profile, _ = Profile.objects.get_or_create(user=user)

        # Get consent value from form ('yes' or 'no')
        consent_value = (request.POST.get("consent") or "").strip().lower()

        # Update consent
        profile.data_sharing_consent = (consent_value == "yes")
        profile.consent_timestamp = timezone.now()
        profile.save()

        # Feedback
        if profile.data_sharing_consent:
            try:
                result = share_user_data_with_insurer(user)
                msg = result.get("message", "Data successfully shared with insurer.")
            except Exception as e:
                msg = f"Error sharing data: {e}"

            messages.success(
                request,
                (
                    "✅ You agreed to share your data on "
                    f"{profile.consent_timestamp:%Y-%m-%d %H:%M}. {msg}"
                ),
            )
        else:
            messages.warning(
                request,
                f"❌ You declined data sharing on {profile.consent_timestamp:%Y-%m-%d %H:%M}.",
            )

        return redirect("usermanagement:consent")


# ======================================================================
# PROVIDER ALERTS PAGE
# ======================================================================

class ProviderAlertsView(LoginRequiredMixin, View):
    """
    Simple view that shows ALL ProviderAlert rows for the current user.

    The AI is triggered separately by /proactive/run-ai/ (in proactive_feat),
    so this view only needs a GET.
    """
    template_name = "usermanagement/provider_alerts.html"

    def get(self, request):
        # Show ALL alerts for this provider, newest first
        alerts = ProviderAlert.objects.filter(user=request.user).order_by("-created_at")
        return render(request, self.template_name, {"alerts": alerts})


# ======================================================================
# PROVIDER REQUESTING DATA SHARING
# ======================================================================

class RequestDataSharingView(LoginRequiredMixin, View):
    """Simulate provider requesting data access from another user (patient)."""

    def post(self, request):
        provider = request.user

        try:
            # For demo purposes: choose the first other user as a "patient"
            patient = User.objects.exclude(id=provider.id).first()
            if not patient:
                messages.error(request, "❌ No other users found in the system.")
                return redirect("usermanagement:provider_alerts")

            # Attempt to share patient data with provider
            result = share_user_data_with_provider(patient, provider)

            # Handle response message
            status = result.get("status")
            if status == "success":
                messages.success(
                    request,
                    result.get("message", "Data shared successfully."),
                )
            elif status == "denied":
                messages.warning(
                    request,
                    result.get("message", "Data sharing was denied."),
                )
            else:
                messages.error(
                    request,
                    result.get("message", "Unknown response received."),
                )

        except Exception as e:
            messages.error(request, f"⚠️ Unexpected error: {e}")

        # Redirect back to dashboard (same as before)
        return redirect("nutrition_dashboard")
