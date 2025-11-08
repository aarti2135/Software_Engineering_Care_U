from django.urls import path
from . import views

app_name = "analytics"

urlpatterns = [
    path("insights/", views.insights, name="insights"),
    path("insights/dismiss/", views.dismiss_highlight, name="dismiss_highlight"),
    path("insights/fragment/", views.insights_fragment, name="insights_fragment"),
    path("charts/data/", views.charts_data, name="charts_data"),  # <-- JSON for charts
]