# usermanagement/views.py
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin

class ProviderAlertsView(LoginRequiredMixin, TemplateView):
    """
    Displays provider alerts for the logged-in user.
    Template: templates/usermanagement/provider_alerts.html
    """
    template_name = "usermanagement/provider_alerts.html"


class ConsentView(LoginRequiredMixin, TemplateView):
    """
    Displays the user's consent management page.
    Template: templates/usermanagement/consent.html
    """
    template_name = "usermanagement/consent.html"
