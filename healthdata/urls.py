from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.HealthDataView.as_view(), name='health_dashboard'),
]