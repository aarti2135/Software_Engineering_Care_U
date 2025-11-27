# proactive_feat/views.py

from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponseRedirect, HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django import forms
from django.utils.http import url_has_allowed_host_and_scheme

from .models import VitalReading, Alert
from usermanagement.models import ProviderAlert
from ai_agent.services import ProviderAlertsAgent
from gamification.services import GamificationService

DASHBOARD_URL = "/api/dashboard/reminders/"


# --------------------------
# Forms
# --------------------------
class VitalForm(forms.ModelForm):
    class Meta:
        model = VitalReading
        fields = ["kind", "value", "measured_at"]


# --------------------------
# Public (ping)
# --------------------------
def ping(_request):
    return HttpResponse("pong")


# --------------------------
# Save a Vital Reading
# --------------------------
@login_required
def vital_form(request):
    if request.method == "POST":
        form = VitalForm(request.POST)
        if form.is_valid():
            vr = form.save(commit=False)
            vr.user = request.user
            vr.save()
            messages.success(request, "Vital saved.")

            next_url = request.POST.get("next") or request.GET.get("next")
            if next_url and url_has_allowed_host_and_scheme(
                next_url, allowed_hosts={request.get_host()}
            ):
                return HttpResponseRedirect(next_url)

            return HttpResponseRedirect(DASHBOARD_URL)

    else:
        form = VitalForm()

    return render(
        request,
        "proactive_feat/vitals_form.html",
        {"form": form, "DASHBOARD_URL": DASHBOARD_URL},
    )


# --------------------------
# Alerts list (HTML)
# --------------------------
@login_required
def alerts_list(request):
    alerts = Alert.objects.filter(user=request.user).order_by("-created_at")[:100]
    return render(
        request,
        "proactive_feat/alerts_list.html",
        {"alerts": alerts, "DASHBOARD_URL": DASHBOARD_URL},
    )


# --------------------------
# UNREAD alerts JSON
# --------------------------
@login_required
def unread_alerts_json(request):
    alerts = (
        Alert.objects.filter(user=request.user, is_read=False, is_dismissed=False)
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


# --------------------------
# 🔥 FULL alerts list JSON (required by Nutrition Dashboard)
# --------------------------
@login_required
def alerts_json(request):
    """
    This returns ALL alerts as a raw JSON array.
    Your JS expects EXACTLY this format: []
    """
    alerts = Alert.objects.filter(user=request.user).order_by("-created_at")

    data = [
        {
            "id": a.id,
            "message": a.message,
            "alert_type": a.alert_type,
            "created_at": a.created_at.isoformat(),
            "is_read": a.is_read,
        }
        for a in alerts
    ]

    return JsonResponse(data, safe=False)


# --------------------------
# Mark alert read
# --------------------------
@login_required
def alert_mark_read(request, pk):
    a = get_object_or_404(Alert, pk=pk, user=request.user)
    a.is_read = True
    a.save()
    return JsonResponse({"ok": True})


# --------------------------
# Launcher
# --------------------------
@login_required
def launcher(request):
    return render(
        request,
        "proactive_feat/launcher.html",
        {"DASHBOARD_URL": DASHBOARD_URL},
    )


# --------------------------
# Home Dashboard
# --------------------------
# --------------------------
# Home Dashboard
# -------------------------

@login_required
def home_dashboard(request):
    from django.utils import timezone
    from healthdata.models import ActivityData, HealthMetrics, Goal
    from gamification.models import UserBadge, Badge

    user = request.user
    today = timezone.localdate()

    today_activity = ActivityData.objects.filter(user=user, date=today).first()
    steps = today_activity.steps if today_activity else 0

    latest_metrics = HealthMetrics.objects.filter(user=user).order_by("-logged_at").first()
    heart_rate = latest_metrics.heart_rate_resting if latest_metrics else 0

    latest_goal = Goal.objects.filter(user=user, status="active").order_by("-created_at").first()

    goal = None
    if latest_goal:
        goal = {
            "title": latest_goal.title or f"{latest_goal.get_goal_type_display()} Goal",
            "notes": latest_goal.notes or f"Target: {latest_goal.target_value}",
        }

    # Initialize ALL variables BEFORE try block
    current_streak = 0
    longest_streak = 0
    total_activities = 0
    badges_earned = 0
    total_badges = 6
    weekly_percentage = 0
    weekly_days_completed = 0
    weekly_goal_target = 7
    badges_data = []

    try:
        print("🟢 Starting gamification service...")
        gamification_service = GamificationService(user)
        gamification_stats = gamification_service.get_user_stats()

        print(f"🟢 Stats retrieved: {gamification_stats}")

        if gamification_stats.get('weekly_progress'):
            weekly_days_completed = gamification_stats['weekly_progress'].days_completed
            weekly_goal_target = gamification_stats['weekly_progress'].goal_target
            if weekly_goal_target > 0:
                weekly_percentage = int((weekly_days_completed / weekly_goal_target) * 100)

        all_badges = Badge.objects.all()
        earned_badge_ids = set(UserBadge.objects.filter(user=user).values_list('badge_id', flat=True))

        for badge in all_badges:
            is_earned = badge.id in earned_badge_ids
            user_badge = None
            if is_earned:
                user_badge = UserBadge.objects.filter(user=user, badge=badge).first()

            badges_data.append({
                'badge': badge,
                'earned': is_earned,
                'earned_at': user_badge.earned_at if user_badge else None,
            })

        current_streak = gamification_stats.get('current_streak', 0)
        longest_streak = gamification_stats.get('longest_streak', 0)
        total_activities = gamification_stats.get('total_activities', 0)
        badges_earned = gamification_stats.get('earned_badge_count', 0)
        total_badges = gamification_stats.get('total_badges', 6)

        print(f"🟢 Final values: streak={current_streak}, activities={total_activities}, badges={badges_earned}")

    except Exception as e:
        import logging
        import traceback
        logging.error(f"Gamification error: {e}")
        logging.error(traceback.format_exc())
        print(f"🔴 ERROR: {e}")
        print(traceback.format_exc())

    return render(
        request,
        "proactive_feat/home_dashboard.html",
        {
            "user_name": user.username,
            "steps": steps,
            "heart_rate": heart_rate,
            "goal": goal,
            "DASHBOARD_URL": DASHBOARD_URL,
            "current_streak": current_streak,
            "longest_streak": longest_streak,
            "total_activities": total_activities,
            "badges_earned": badges_earned,
            "total_badges": total_badges,
            "weekly_percentage": weekly_percentage,
            "weekly_days_completed": weekly_days_completed,
            "weekly_goal_target": weekly_goal_target,
            "badges_data": badges_data,
        },
    )
# --------------------------
# AI Provider Scan
# --------------------------
@login_required
def run_ai_now(request):
    provider_profile = getattr(request.user, "profile", None)

    if not provider_profile or not getattr(provider_profile, "is_provider", False):
        messages.error(request, "Only healthcare providers can run AI alerts.")
        return redirect("usermanagement:provider_alerts")

    agent = ProviderAlertsAgent(provider_user=request.user)
    result = agent.run_for_user(request.user, days=7)

    created = result.get("created_alerts", 0)
    status = result.get("status", "unknown")

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

    return redirect("usermanagement:provider_alerts")
