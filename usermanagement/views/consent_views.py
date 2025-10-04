from django.shortcuts import render, redirect
from django.views import View
from django.contrib import messages
from usermanagement.models.custom_user import CustomUser
from usermanagement.Utils import share_user_data_with_insurer


class ConsentView(View):
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
        user_id = request.POST.get("user_id")
        consent_given = request.POST.get("consent") == "yes"

        try:
            user = CustomUser.objects.get(pk=user_id)
        except CustomUser.DoesNotExist:
            messages.error(request, "User not found.")
            return redirect("consent")

        # Save consent status
        user.data_sharing_consent = consent_given
        user.save()

        # Optional: call util function if consent granted
        if consent_given:
            result = share_user_data_with_insurer(user_id)
            messages.success(request, result["message"])
        else:
            messages.warning(request, "You declined to share anonymized data.")

        return redirect("consent")
