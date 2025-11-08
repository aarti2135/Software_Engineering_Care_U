from django.views import View
from django.shortcuts import render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.contrib.auth import get_user_model
from usermanagement.models import ProviderAlert
from usermanagement.utils import detect_health_patterns, share_user_data_with_provider
from healthdata.ai_agent import evaluate_user

User = get_user_model()


class ProviderAlertsView(LoginRequiredMixin, View):
    """Display health alerts for the current user (acting as provider)."""
    template_name = "usermanagement/provider_alerts.html"

    def get(self, request):
        user = request.user


        # ✅ Run the new AI agent (creates alerts if needed)
        evaluate_user(user)

        # Run pattern detection on current user's data
        detect_health_patterns(user)

        # Get all alerts for current user
        alerts = ProviderAlert.objects.filter(
            user=user
        ).order_by('-created_at')

        return render(request, self.template_name, {"alerts": alerts})

    def post(self, request):
        """
        Clicking 'Run AI now' calls the agent immediately.
        Stays on the same page and shows a toast/flash message.
        """
        user = request.user
        created = evaluate_user(user)  # your function can return a count or None

        if created:
            messages.success(request, f"AI ran successfully and created {created} new alert(s).")
        else:
            messages.info(request, "AI ran successfully. No new alerts were needed.")
        return redirect("provider_alerts")

class RequestDataSharingView(LoginRequiredMixin, View):
    """Simulate requesting data from another user (patient)."""

    def post(self, request):
        provider = request.user

        try:
            # In production, you'd select a specific patient
            # For demo: just grab another user
            patient = User.objects.exclude(id=provider.id).first()

            if not patient:
                messages.error(request, "No other users found in system.")
                return redirect('provider_alerts')

            # Attempt to share data
            result = share_user_data_with_provider(patient, provider)

            # Display result
            if result["status"] == "success":
                messages.success(request, result["message"])
            elif result["status"] == "denied":
                messages.warning(request, result["message"])
            else:
                messages.error(request, result["message"])

        except Exception as e:
            messages.error(request, f"Unexpected error: {e}")

        return redirect('nutrition_dashboard')
