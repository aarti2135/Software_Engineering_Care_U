from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView

urlpatterns = [
    path(
        "",
        TemplateView.as_view(
            template_name="index.html",
            extra_context={
                "cards": [
                    {"title": "Nutrition", "desc": "Calories & macros", "url": "/api/nutrition/"},
                    {"title": "Glucose", "desc": "Track glucose levels", "url": "/api/glucose/"},
                    {"title": "Medication", "desc": "Dosage & timing", "url": "/api/medication/"},
                    {"title": "Doctor Notes", "desc": "Secure notes", "url": "/api/doctornotes/"},
                ]
            },
        ),
        name="home",
    ),
    path("admin/", admin.site.urls),
    path("api/", include("healthlog.urls")),
]
