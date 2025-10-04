from django.urls import path
from usermanagement.views.consent_views import ConsentView

urlpatterns = [
    path('consent/', ConsentView.as_view(), name='consent'),
]
