from django.urls import path
from django.contrib.auth.views import LogoutView
from . import views

app_name = "proactive_feat"

urlpatterns = [
    # --------------------------------------------------
    # Existing routes
    # --------------------------------------------------
    path("ping/", views.ping, name="pro_ping"),
    path("vitals/new/", views.vital_form, name="pro_vital_form"),
    path("alerts/", views.alerts_list, name="pro_alerts_list"),
    path("alerts/unread/", views.unread_alerts_json, name="pro_alerts_unread"),
    path("alerts/mark-read/<int:pk>/", views.alert_mark_read, name="pro_alert_mark_read"),
    path("", views.launcher, name="pro_launcher"),

    # --------------------------------------------------
    # Home dashboard for Epic 7
    # --------------------------------------------------
    path("dashboard/", views.home_dashboard, name="home_dashboard"),

    # --------------------------------------------------
    # AI Agent (Epic 7 – Part 3)
    # IMPORTANT: This must match the NEW view name
    # --------------------------------------------------
    path("run-ai/", views.run_ai_now, name="run_ai_now"),

    # --------------------------------------------------
    # Logout
    # --------------------------------------------------
    path("logout/", LogoutView.as_view(), name="logout"),
    path("accounts/logout/", LogoutView.as_view(), name="accounts_logout"),
]
