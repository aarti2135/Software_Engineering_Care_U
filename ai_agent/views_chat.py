from django.contrib.auth.decorators import login_required
from django.shortcuts import render


@login_required
def chat_dashboard(request):
    """
    Basic AI chat page shell.

    For now this just renders an empty chat layout; the actual interactive
    chat UI and JS wiring will be added in later steps.
    """
    return render(request, "ai_agent/chat_dashboard.html")


