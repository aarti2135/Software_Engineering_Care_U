from django.shortcuts import render, redirect
from django.views import View
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils import timezone
from usermanagement.utils import share_user_data_with_insurer


class ConsentView(LoginRequiredMixin, View):
    """Handle user consent for data sharing."""
    template_name = "usermanagement/consent.html"

    def get(self, request):
        """Render consent form with current status."""
        profile = request.user.profile
        context = {
            'current_consent': profile.data_sharing_consent,
            'consent_date': profile.consent_timestamp
        }
        return render(request, self.template_name, context)

    def post(self, request):
        """Handle consent form submission."""
        user = request.user
        profile = user.profile
        consent_value = request.POST.get("consent")  # 'agree' or 'disagree'

        # Update consent status
        profile.data_sharing_consent = (consent_value == "agree")
        profile.consent_timestamp = timezone.now()
        profile.save()

        # If agreed, trigger data sharing
        if profile.data_sharing_consent:
            result = share_user_data_with_insurer(user)
            messages.success(
                request,
                f"✅ You agreed to share data on {profile.consent_timestamp:%Y-%m-%d %H:%M}. "
                f"{result['message']}"
            )
        else:
            messages.warning(
                request,
                f"❌ You declined data sharing on {profile.consent_timestamp:%Y-%m-%d %H:%M}."
            )

        return redirect("consent")