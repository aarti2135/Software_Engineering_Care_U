from django.views import View
from django.shortcuts import render, redirect   # ✅ added redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages              # ✅ added messages
from usermanagement.models import ProviderAlert, CustomUser  # ✅ added CustomUser
from usermanagement.Utils import detect_health_patterns, share_user_data_with_provider  # ✅ added share_user_data_with_provider


class ProviderAlertsView(LoginRequiredMixin, View):
    template_name = "usermanagement/provider_alerts.html"

    def get(self, request):
        user = request.user
        # Run detection for the current user
        detect_health_patterns(user)
        alerts = ProviderAlert.objects.filter(user=user).order_by('-created_at')
        return render(request, self.template_name, {"alerts": alerts})


class RequestDataSharingView(View):
    def post(self, request):
        provider = request.user
        try:
            # Simulate selecting another user (patient)
            patient = CustomUser.objects.exclude(id=provider.id).first()
            if not patient:
                messages.error(request, "No other user found to share data with.")
                return redirect('nutrition_dashboard')

            # Attempt to share anonymized data (using your utils function)
            result = share_user_data_with_provider(patient.id, provider.id)

            # Show feedback based on result
            if result.get("status") == "success":
                messages.success(request, result.get("message"))
            else:
                messages.warning(request, result.get("message"))

        except Exception as e:
            messages.error(request, f"Error: {e}")

        return redirect('provider_alerts')
