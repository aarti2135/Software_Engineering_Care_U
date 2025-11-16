"""
URL configuration for AI Agent app
"""

from django.urls import path
from . import views
from . import views_chat

app_name = 'ai_agent'

urlpatterns = [
    # API endpoint for the agent
    path('chat/', views.ChatAPIView.as_view(), name='chat'),

    # Full-page chat UI
    path('chat/dashboard/', views_chat.chat_dashboard, name='chat_dashboard'),
]

