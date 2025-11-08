from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView
urlpatterns = [
    path("proactive/ping/", views.ping, name="pro_ping"),
    path("proactive/vitals/new/", views.vital_form, name="pro_vital_form"),
    path("proactive/alerts/", views.alerts_list, name="pro_alerts_list"),
    path("proactive/alerts/unread/", views.unread_alerts_json, name="pro_alerts_unread"),
    path("proactive/alerts/mark-read/<int:pk>/", views.alert_mark_read, name="pro_alert_mark_read"),
    path("proactive/", views.launcher, name="pro_launcher"),    path("logout/", LogoutView.as_view(), name="logout"),               # <- adds the name base.html expects
    path("accounts/logout/", LogoutView.as_view(), name="accounts_logout"),
]
