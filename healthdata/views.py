from django.shortcuts import render

# Create your views here.
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView
from .models import HealthData, HealthPrivacySettings
from usermanagement.models import CustomUser  # Reference teammate's work


class HealthDataView(LoginRequiredMixin, ListView):
    model = HealthData
    template_name = 'healthdata/dashboard.html'

    def get_queryset(self):
        # DOUBLE SECURITY: Check both general consent AND granular controls
        user = self.request.user

        # First, check if user gave general consent (teammate's field)
        if not user.data_sharing_consent:
            return HealthData.objects.none()  # Show nothing if no general consent

        # Then apply your granular filters
        privacy_settings = HealthPrivacySettings.objects.get(user=user)
        # Add granular filtering logic here

        return HealthData.objects.filter(user=user)