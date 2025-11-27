from django.contrib.auth.decorators import login_required
from django.shortcuts import render


@login_required
def chat_dashboard(request):
    """
    AI chat page.
    """
    return render(request, "ai_agent/chat_dashboard.html")


