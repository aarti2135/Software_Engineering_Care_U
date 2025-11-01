from django.urls import path
from usermanagement.views.consent_views import ConsentView
from usermanagement.views.health_alerts_views import ProviderAlertsView, RequestDataSharingView

urlpatterns = [
    # Consent page (patient)
    path('consent/', ConsentView.as_view(), name='consent'),

    # Provider alerts page (provider)
    path('provider/alerts/', ProviderAlertsView.as_view(), name='provider_alerts'),

    # Request data sharing (button on dashboard)
    path('request-sharing/', RequestDataSharingView.as_view(), name='request-sharing'),
]
