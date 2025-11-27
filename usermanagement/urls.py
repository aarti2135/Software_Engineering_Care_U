# usermanagement/urls.py
from django.urls import path
from . import views

# Namespace so {% url 'usermanagement:...' %} works in templates
app_name = "usermanagement"

urlpatterns = [
    # Provider Alerts page (AI-assisted recommendations)
    path("provider_alerts/", views.ProviderAlertsView.as_view(), name="provider_alerts"),

    # Consent page (user data-sharing preferences)
    path("consent/", views.ConsentView.as_view(), name="consent"),

    # Request data sharing (button on dashboard)
    path("request-sharing/", views.RequestDataSharingView.as_view(), name="request-sharing"),
]