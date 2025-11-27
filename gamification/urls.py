from django.urls import path
from . import views

app_name = 'gamification'

urlpatterns = [
    path('rewards/', views.rewards_dashboard, name='rewards_dashboard'),
    path('api/stats/', views.get_gamification_stats, name='get_stats'),
]