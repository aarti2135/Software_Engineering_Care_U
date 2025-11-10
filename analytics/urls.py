# analytics/urls.py
from django.urls import path
from . import views

app_name = "analytics"

urlpatterns = [
    # ✅ Main dashboard page (Analytics view)
    path("", views.analytics_dashboard, name="analytics_dashboard"),

    # ✅ Charts JSON data endpoint
    path("charts/data/", views.charts_data, name="charts_data"),

    # ✅ Insights (AI / health highlights)
    path("insights/", views.insights, name="insights"),
    path("insights/fragment/", views.insights_fragment, name="insights_fragment"),
    path("insights/dismiss/", views.dismiss_highlight, name="dismiss_highlight"),
]
