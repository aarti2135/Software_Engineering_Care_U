# proactive_feat/views.py

from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponseRedirect, HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django import forms
from django.utils.http import url_has_allowed_host_and_scheme  # for safe redirects

# where to go "back to dashboard"
DASHBOARD_URL = "/api/dashboard/reminders/"

from .models import VitalReading, Alert
from usermanagement.models import ProviderAlert  # (not used directly now, but ok to keep)
from ai_agent.services import ProviderAlertsAgent


# ---------- Forms ----------
class VitalForm(forms.ModelForm):
    class Meta:
        model = VitalReading
        fields = ["kind", "value", "measured_at"]


# ---------- Public (no auth) ----------
def ping(_request):
    # Simple health check for URL wiring
    return HttpResponse("pong")


# ---------- Auth-required views ----------
@login_required
def vital_form(request):
    if request.method == "POST":
        form = VitalForm(request.POST)
        if form.is_valid():
            vr = form.save(commit=False)
            vr.user = request.user
            vr.save()
            messages.success(request, "Vital saved.")

            # Prefer ?next= or posted next= if safe; else go to dashboard
            next_url = request.POST.get("next") or request.GET.get("next")
            if next_url and url_has_allowed_host_and_scheme(
                next_url,
                allowed_hosts={request.get_host()},
            ):
                return HttpResponseRedirect(next_url)

            return HttpResponseRedirect(DASHBOARD_URL)
    else:
        form = VitalForm()

    # Pass DASHBOARD_URL so template can render a Back button
    return render(
        request,
        "proactive_feat/vitals_form.html",
        {"form": form, "DASHBOARD_URL": DASHBOARD_URL},
    )


@login_required
def alerts_list(request):
    alerts = Alert.objects.filter(user=request.user).order_by("-created_at")[:100]
    return render(
        request,
        "proactive_feat/alerts_list.html",
        {"alerts": alerts, "DASHBOARD_URL": DASHBOARD_URL},
    )


@login_required
def unread_alerts_json(request):
    alerts = (
        Alert.objects.filter(
            user=request.user,
            is_read=False,
            is_dismissed=False,
        )
        .order_by("-created_at")[:10]
    )
    data = [
        {
            "id": a.id,
            "type": a.alert_type,
            "message": a.message,
            "ts": a.created_at.isoformat(),
        }
        for a in alerts
    ]
    return JsonResponse({"alerts": data})


@login_required
def alert_mark_read(request, pk):
    a = get_object_or_404(Alert, pk=pk, user=request.user)
    a.is_read = True
    a.save()
    return JsonResponse({"ok": True})


@login_required
def launcher(request):
    return render(
        request,
        "proactive_feat/launcher.html",
        {"DASHBOARD_URL": DASHBOARD_URL},
    )


# ---------- Home Dashboard ----------
@login_required
def home_dashboard(request):
    """
    Displays the main home dashboard with user info,
    steps, heart rate, and latest goal.
    """
    from django.utils import timezone
    from healthdata.models import ActivityData, HealthMetrics, Goal

    user = request.user
    today = timezone.localdate()

    # Get today's steps from ActivityData
    today_activity = ActivityData.objects.filter(
        user=user,
        date=today,
    ).first()
    steps = today_activity.steps if today_activity else 0

    # Get most recent heart rate from HealthMetrics
    latest_metrics = (
        HealthMetrics.objects.filter(user=user)
        .order_by("-logged_at")
        .first()
    )
    heart_rate = latest_metrics.heart_rate_resting if latest_metrics else 0

    # Get the latest active goal
    latest_goal = (
        Goal.objects.filter(user=user, status="active")
        .order_by("-created_at")
        .first()
    )

    # Format goal data for template
    goal = None
    if latest_goal:
        goal = {
            "title": latest_goal.title
            or f"{latest_goal.get_goal_type_display()} Goal",
            "notes": latest_goal.notes
            or f"Target: {latest_goal.target_value}",
        }

    return render(
        request,
        "proactive_feat/home_dashboard.html",
        {
            "user_name": user.username,
            "steps": steps,
            "heart_rate": heart_rate,
            "goal": goal,
            "DASHBOARD_URL": DASHBOARD_URL,
        },
    )


# ---------- NEW: Provider AI Scan (Epic 7 – part 3) ----------
@login_required
def run_ai_now(request):
    """
    Provider clicks 'Run AI Now' to scan nutrition data with AI.

    Uses ProviderAlertsAgent to:
      - Create DAILY alerts (one per day with data)
      - Create a WEEKLY AI summary alert

    For now, we run the agent for the current user as the patient.
    """

    provider_profile = getattr(request.user, "profile", None)

    # 1) Security: only providers can run this
    if not provider_profile or not getattr(provider_profile, "is_provider", False):
        messages.error(request, "Only healthcare providers can run AI alerts.")
        return redirect("usermanagement:provider_alerts")

    # 2) Create the agent for this provider
    agent = ProviderAlertsAgent(provider_user=request.user)

    # 3) Run AI for the current user as the patient (days=7 window)
    result = agent.run_for_user(request.user, days=7)

    created = result.get("created_alerts", 0)
    status = result.get("status", "unknown")

    # 4) Feedback to provider
    if created > 0:
        messages.success(
            request,
            f"AI scan complete. {created} alert(s) created. Status: {status}.",
        )
    else:
        messages.info(
            request,
            f"AI scan complete. No new alerts created. Status: {status}.",
        )

    # 5) Back to provider alerts page
    return redirect("usermanagement:provider_alerts")
