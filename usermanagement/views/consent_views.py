# usermanagement/views/consent_views.py
from django.shortcuts import render, redirect
from django.views import View
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils import timezone

from usermanagement.utils import share_user_data_with_insurer
from usermanagement.models import Profile  # Ensure this model exists


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

        # ✅ FIX: use namespaced redirect
        return redirect("usermanagement:consent")
