# analytics/views.py
from datetime import timedelta
from collections import defaultdict
from urllib.parse import urlparse

from django.apps import apps
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseBadRequest
from django.shortcuts import render, redirect
from django.utils import timezone

from .models import DismissedHighlight
from .services import compute_highlights


# --------------------------------------------------------------------
# 🔹 Demo highlights when no real data exists (DEBUG mode)
# --------------------------------------------------------------------
def _demo_highlights_if_empty(highlights):
    """Show placeholder insights when there's no real data (only in DEBUG mode)."""
    if highlights or not getattr(settings, "DEBUG", False):
        return highlights
    return [
        {
            "key": "high_glucose",
            "title": "High Glucose Detected",
            "message": "Your average glucose exceeded 180 mg/dL on 2+ recent days.",
            "doctor_hint": True,
            "why": "Sustained high glucose can increase complication risk.",
            "actions": ["Log meals", "Hydrate", "Discuss with your provider if this continues"],
        },
        {
            "key": "low_sleep",
            "title": "Low Sleep",
            "message": "Average sleep fell below 5.5 hours for 3+ days.",
            "doctor_hint": False,
            "why": "Short sleep affects mood, glucose, and activity.",
            "actions": ["Keep a fixed bedtime", "Reduce late-night screens"],
        },
        {
            "key": "activity_drop",
            "title": "Activity Drop",
            "message": "Steps dropped >40% vs your 30-day baseline.",
            "doctor_hint": False,
            "why": "A sudden drop can impact energy and glucose control.",
            "actions": ["Take a 10-minute walk after meals"],
        },
    ]


# --------------------------------------------------------------------
# 🔹 Insights (highlights)
# --------------------------------------------------------------------
@login_required
def insights(request):
    """Standalone page showing up to 3 health insights."""
    raw = compute_highlights(request.user, limit=10) or []
    visible = [h for h in raw if not DismissedHighlight.is_hidden(request.user, h["key"])]
    visible = _demo_highlights_if_empty(visible[:3])

    return render(request, "analytics/insights.html", {
        "highlights": visible,
        "doctor_suggest": any(h.get("doctor_hint") for h in visible),
    })


@login_required
def insights_fragment(request):
    """Return only the insights card fragment for dashboard embedding."""
    raw = compute_highlights(request.user, limit=10) or []
    visible = [h for h in raw if not DismissedHighlight.is_hidden(request.user, h["key"])]
    visible = _demo_highlights_if_empty(visible[:3])

    return render(request, "analytics/_cards.html", {
        "highlights": visible,
        "doctor_suggest": any(h.get("doctor_hint") for h in visible),
    })


@login_required
def dismiss_highlight(request):
    """Dismiss a highlight for 48 hours and redirect to previous page."""
    if request.method != "POST":
        return HttpResponseBadRequest("Invalid method")

    key = request.POST.get("key")
    if key not in {"high_glucose", "low_sleep", "activity_drop"}:
        return HttpResponseBadRequest("Invalid key")

    DismissedHighlight.dismiss_for_48h(request.user, key)

    # Redirect user back safely
    nxt = request.GET.get("next")
    if nxt:
        return redirect(nxt)

    ref = request.META.get("HTTP_REFERER")
    try:
        if ref and urlparse(ref).netloc:
            return redirect(ref)
    except Exception:
        pass

    return redirect("analytics:insights")


# --------------------------------------------------------------------
# 🔹 Charts (glucose / sleep / steps)
# --------------------------------------------------------------------
@login_required
def charts_data(request):
    """
    Returns JSON time series for analytics charts:
      • Glucose (mg/dL): average per day
      • Sleep (hours):   average per day
      • Steps:           sum per day
    """
    user = request.user

    # Dynamic date range
    try:
        days = max(7, int(request.GET.get("days", 14)))
    except Exception:
        days = 14

    end = timezone.localdate()
    start = end - timedelta(days=days - 1)
    day_list = [start + timedelta(days=i) for i in range(days)]
    labels = [d.strftime("%b %d") for d in day_list]

    # Load health models dynamically
    GlucoseEntry = apps.get_model("healthdata", "GlucoseEntry")
    SleepData = apps.get_model("healthdata", "SleepData")
    ActivityData = apps.get_model("healthdata", "ActivityData")

    # -------- Glucose (avg per day) --------
    g_bucket = defaultdict(list)
    for created_at, val in (
        GlucoseEntry.objects
        .filter(user=user, created_at__date__gte=start, created_at__date__lte=end)
        .values_list("created_at", "glucose_mg_dl")
    ):
        if created_at and val is not None:
            g_bucket[timezone.localtime(created_at).date()].append(float(val))

    glucose = [
        round(sum(vals) / len(vals), 1) if vals else 0.0
        for vals in (g_bucket.get(d, []) for d in day_list)
    ]

    # -------- Sleep (avg per day) --------
    s_bucket = defaultdict(list)
    for d0, mins in (
        SleepData.objects
        .filter(user=user, date__gte=start, date__lte=end)
        .values_list("date", "total_sleep_minutes")
    ):
        if d0 and mins is not None:
            s_bucket[d0].append(float(mins))

    sleep_raw = [
        round(sum(vals) / len(vals), 2) if vals else 0.0
        for vals in (s_bucket.get(d, []) for d in day_list)
    ]
    max_raw = max(sleep_raw) if sleep_raw else 0.0
    sleep = (
        [round(v, 1) for v in sleep_raw]
        if max_raw <= 24
        else [round(v / 60.0, 1) for v in sleep_raw]
    )

    # -------- Steps (sum per day) --------
    a_bucket = defaultdict(int)
    for d0, steps in (
        ActivityData.objects
        .filter(user=user, date__gte=start, date__lte=end)
        .values_list("date", "steps")
    ):
        if d0 and steps is not None:
            a_bucket[d0] += int(steps)

    steps = [a_bucket.get(d, 0) for d in day_list]

    empty = not (any(glucose) or any(sleep) or any(steps))

    return JsonResponse({
        "empty": empty,
        "labels": labels,
        "glucose": glucose,
        "sleep": sleep,
        "steps": steps,
    })


# --------------------------------------------------------------------
# 🔹 Main Analytics Dashboard View
# --------------------------------------------------------------------
@login_required
def analytics_dashboard(request):
    """Main Analytics dashboard page (charts & insights)."""
    return render(request, "analytics/analytics_dashboard.html")
