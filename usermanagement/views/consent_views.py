from django.shortcuts import render, redirect
from django.views import View
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from usermanagement.models import CustomUser
from usermanagement.Utils import share_user_data_with_insurer
from django.utils import timezone


class ConsentView(LoginRequiredMixin, View):
    template_name = "usermanagement/consent.html"

    def get(self, request):
        """
        Render the consent form page.
        """
        return render(request, self.template_name)

    def post(self, request):
        """
        Handle form submission when user agrees or disagrees.
        """

        user = request.user
        consent_value = request.POST.get("consent")  # 'agree' or 'disagree'

        try:

            custom_user = CustomUser.objects.get(pk=user.pk)
        except CustomUser.DoesNotExist:
            messages.error(request, "User not found.")
            return redirect("consent")

         # Save consent status
        custom_user.data_sharing_consent = (consent_value == "agree")
        custom_user.consent_timestamp = timezone.now()
        custom_user.save()


        if custom_user.data_sharing_consent:
            share_user_data_with_insurer(custom_user)
            messages.success(
                request,
                f"You agreed to share anonymized data on {custom_user.consent_timestamp:%Y-%m-%d %H:%M}."
            )
        else:
            messages.warning(
                request,
                f"You declined data sharing on {custom_user.consent_timestamp:%Y-%m-%d %H:%M}."
            )

        return redirect("consent")
