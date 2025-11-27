# proactive_feat/urls.py

from django.urls import path
from django.contrib.auth.views import LogoutView
from . import views

app_name = "proactive_feat"

urlpatterns = [
    # Basic
    path("ping/", views.ping, name="pro_ping"),

    # Vitals
    path("vitals/new/", views.vital_form, name="pro_vital_form"),

    # Alerts (HTML list)
    path("alerts/", views.alerts_list, name="pro_alerts_list"),

    # Unread alerts JSON
    path("alerts/unread/", views.unread_alerts_json, name="pro_alerts_unread"),

    # 🔥 FULL alerts JSON (needed by Nutrition Dashboard)
    path("alerts/json", views.alerts_json, name="pro_alerts_json"),

    # Mark alert read
    path("alerts/mark-read/<int:pk>/", views.alert_mark_read, name="pro_alert_mark_read"),

    # Launcher
    path("", views.launcher, name="pro_launcher"),

    # Dashboard
    path("dashboard/", views.home_dashboard, name="home_dashboard"),

    # AI Agent
    path("run-ai/", views.run_ai_now, name="run_ai_now"),

    # Logout
    path("logout/", LogoutView.as_view(), name="logout"),
    path("accounts/logout/", LogoutView.as_view(), name="accounts_logout"),
]
