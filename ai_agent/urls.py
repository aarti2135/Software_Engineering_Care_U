"""
URL configuration for AI Agent app
"""

from django.urls import path
from . import views

app_name = 'ai_agent'

urlpatterns = [
    path('chat/', views.ChatAPIView.as_view(), name='chat'),
]

