# usermanagement/urls.py
from django.urls import path

# ✅ Correct imports (based on your folder structure)
from usermanagement.views.health_alerts_views import ProviderAlertsView
from usermanagement.views.consent_views import ConsentView

# ✅ Namespace so {% url 'usermanagement:...' %} works in templates
app_name = "usermanagement"

urlpatterns = [
    # 🔹 Provider Alerts page (AI-assisted recommendations)
    path("provider_alerts/", ProviderAlertsView.as_view(), name="provider_alerts"),

    # 🔹 Consent page (user data-sharing preferences)
    path("consent/",ConsentView.as_view(),name="consent"),
]
