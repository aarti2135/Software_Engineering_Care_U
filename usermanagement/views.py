# usermanagement/views.py
from django.shortcuts import render, redirect
from django.views import View
from django.views.generic import TemplateView
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import get_user_model
from django.utils import timezone

from usermanagement.utils import (
    share_user_data_with_insurer,
    detect_health_patterns,
    share_user_data_with_provider
)
from usermanagement.models import Profile, ProviderAlert
from healthdata.ai_agent import evaluate_user

User = get_user_model()


# ============================================================================
# CONSENT MANAGEMENT
# ============================================================================

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
                f"✅ You agreed to share your data on "
                f"{profile.consent_timestamp:%Y-%m-%d %H:%M}. {msg}"
            )
        else:
            messages.warning(
                request,
                f"❌ You declined data sharing on {profile.consent_timestamp:%Y-%m-%d %H:%M}."
            )

        return redirect("usermanagement:consent")


# ============================================================================
# PROVIDER ALERTS & HEALTH ANALYSIS
# ============================================================================

class ProviderAlertsView(LoginRequiredMixin, View):
    """Display and analyze provider AI health alerts for the current user."""
    template_name = "usermanagement/provider_alerts.html"

    def get(self, request):
        """Display all alerts and allow the user to trigger the AI scan."""
        user = request.user

        # Run AI analysis to ensure alerts are updated (safe version)
        try:
            evaluate_user(user)
        except Exception as e:
            print(f"⚠️ AI evaluation failed: {e}")

        # Pattern detection (non-blocking)
        try:
            detect_health_patterns(user)
        except Exception as e:
            print(f"⚠️ Pattern detection failed: {e}")

        # Fetch all provider alerts for the current user
        alerts = ProviderAlert.objects.filter(user=user).order_by('-created_at')

        context = {
            "alerts": alerts,
        }
        return render(request, self.template_name, context)

    def post(self, request):
        """Handle 'Run AI Now' button → triggers AI and reloads page with message."""
        user = request.user

        try:
            created = evaluate_user(user)  # Can return alert count
            if created:
                messages.success(
                    request,
                    f"🤖 AI ran successfully and generated {created} new alert(s)."
                )
            else:
                messages.info(
                    request,
                    "✅ AI ran successfully --- no new alerts were needed."
                )
        except Exception as e:
            messages.error(request, f"⚠️ Error while running AI: {e}")

        return redirect("usermanagement:provider_alerts")


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
            if result.get("status") == "success":
                messages.success(request, result.get("message", "Data shared successfully."))
            elif result.get("status") == "denied":
                messages.warning(request, result.get("message", "Data sharing was denied."))
            else:
                messages.error(request, result.get("message", "Unknown response received."))

        except Exception as e:
            messages.error(request, f"⚠️ Unexpected error: {e}")

        # Redirect back to dashboard
        return redirect("nutrition_dashboard")