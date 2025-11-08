# analytics/views.py

from datetime import date, timedelta
from collections import defaultdict
from urllib.parse import urlparse

from django.conf import settings
from django.apps import apps
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseBadRequest
from django.shortcuts import render, redirect

from .models import DismissedHighlight
from .services import compute_highlights


# --------------------------------------------------------------------
# Optional demo highlights (only show when DEBUG=True and nothing real)
# --------------------------------------------------------------------
def _demo_highlights_if_empty(highlights):
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
            "why": "Short sleep affects mood, glucose and activity.",
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
# Highlights (cards) + dismiss
# --------------------------------------------------------------------
@login_required
def insights(request):
    """
    Standalone page (optional). Shows up to 3 highlights.
    Dismissed items are hidden for 48 hours.
    """
    raw = compute_highlights(request.user, limit=10) or []
    visible = [h for h in raw if not DismissedHighlight.is_hidden(request.user, h["key"])]
    visible = _demo_highlights_if_empty(visible[:3])
    return render(request, "analytics/insights.html", {
        "highlights": visible,
        "doctor_suggest": any(h.get("doctor_hint") for h in visible),
    })


@login_required
def insights_fragment(request):
    """
    Fragment used by the dashboard. Returns only the cards HTML.
    """
    raw = compute_highlights(request.user, limit=10) or []
    visible = [h for h in raw if not DismissedHighlight.is_hidden(request.user, h["key"])]
    visible = _demo_highlights_if_empty(visible[:3])
    return render(request, "analytics/_cards.html", {
        "highlights": visible,
        "doctor_suggest": any(h.get("doctor_hint") for h in visible),
    })


@login_required
def dismiss_highlight(request):
    """
    POST: hide a highlight for 48 hours, then return to the same page.
    Keys supported by your service: high_glucose, low_sleep, activity_drop.
    """
    if request.method != "POST":
        return HttpResponseBadRequest("Invalid method")

    key = request.POST.get("key")
    if key not in {"high_glucose", "low_sleep", "activity_drop"}:
        return HttpResponseBadRequest("Invalid key")

    DismissedHighlight.dismiss_for_48h(request.user, key)

    # Redirect back to where the user was (dashboard or insights)
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
# Charts JSON (glucose/sleep/steps) + 7-day averages
# --------------------------------------------------------------------
# analytics/views.py
# analytics/views.py
from datetime import date, timedelta
from collections import defaultdict
from django.apps import apps
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

@login_required
def charts_data(request):
    """
    Return time series for the charts only (no donut, no averages).
      - Glucose (mg/dL): daily average from GlucoseEntry.created_at
      - Sleep (hours):   auto-detects if total_sleep_minutes are in hours or minutes
      - Steps:           daily sum
    """
    user = request.user
    try:
        days = max(7, int(request.GET.get("days", 14)))
    except Exception:
        days = 14

    end = date.today()
    start = end - timedelta(days=days - 1)
    day_list = [start + timedelta(days=i) for i in range(days)]
    labels = [d.strftime("%b %d") for d in day_list]

    GlucoseEntry = apps.get_model("healthdata", "GlucoseEntry")
    SleepData    = apps.get_model("healthdata", "SleepData")
    ActivityData = apps.get_model("healthdata", "ActivityData")

    # -------- Glucose: avg per day --------
    g_bucket = defaultdict(list)
    qs_g = (GlucoseEntry.objects
            .filter(user=user, created_at__date__gte=start, created_at__date__lte=end)
            .values_list("created_at", "glucose_mg_dl"))
    for created_at, val in qs_g:
        if created_at and val is not None:
            g_bucket[created_at.date()].append(float(val))

    glucose = []
    for d0 in day_list:
        vals = g_bucket.get(d0, [])
        glucose.append(round(sum(vals) / len(vals), 1) if vals else 0.0)

    # -------- Sleep: avg per day (auto-detect units) --------
    s_bucket = defaultdict(list)
    qs_s = (SleepData.objects
            .filter(user=user, date__gte=start, date__lte=end)
            .values_list("date", "total_sleep_minutes"))
    for d0, mins in qs_s:
        if d0 and mins is not None:
            s_bucket[d0].append(float(mins))

    # raw daily averages (could already be hours)
    sleep_raw = []
    for d0 in day_list:
        vals = s_bucket.get(d0, [])
        sleep_raw.append(round(sum(vals) / len(vals), 2) if vals else 0.0)

    # If values look like hours (<=24), keep; else convert minutes→hours
    max_raw = max(sleep_raw) if sleep_raw else 0.0
    sleep = [round(v, 1) for v in sleep_raw] if max_raw <= 24 else [round(v / 60.0, 1) for v in sleep_raw]

    # -------- Steps: sum per day --------
    a_bucket = defaultdict(int)
    qs_a = (ActivityData.objects
            .filter(user=user, date__gte=start, date__lte=end)
            .values_list("date", "steps"))
    for d0, steps in qs_a:
        if d0 and steps is not None:
            a_bucket[d0] += int(steps)

    steps = [a_bucket.get(d0, 0) for d0 in day_list]

    empty = not (any(glucose) or any(sleep) or any(steps))

    return JsonResponse({
        "empty": empty,
        "labels": labels,
        "glucose": glucose,
        "sleep": sleep,
        "steps": steps,
    })
