from datetime import date, timedelta
from django.db.models import Avg
from django.utils import timezone
from healthdata.models import GlucoseEntry, SleepData, ActivityData

def _daterange(days_back):
    today = date.today()
    return today - timedelta(days=days_back-1), today

def compute_highlights(user, limit=3):
    """
    Returns a list of dicts like:
    [{
      "key": "high_glucose" | "low_sleep" | "activity_drop",
      "title": "High Glucose",
      "detail": "Average > 180 mg/dL for 2+ days in the last week.",
      "doctor_hint": True/False
    }, ...] (max length = limit)
    """
    highlights = []

    # ---- Glucose: average > 180 mg/dL for 2 or more days (look back 7 days)
    start7, end7 = _daterange(7)
    gqs = (GlucoseEntry.objects
           .filter(user=user, created_at__date__range=(start7, end7))
           .values('created_at__date')
           .annotate(avg=Avg('glucose_mg_dl')))
    high_days = sum(1 for g in gqs if (g['avg'] or 0) > 180.0)
    if high_days >= 2:
        highlights.append({
            "key": "high_glucose",
            "title": "High Glucose",
            "detail": f"Average glucose > 180 mg/dL on {high_days} day(s) this week.",
            "doctor_hint": True
        })

    # ---- Sleep: average sleep < 5.5 hours for 3 or more days (look back 7 days)
    s_qs = (SleepData.objects
            .filter(user=user, date__range=(start7, end7))
            .values('date')
            .annotate(avg=Avg('total_sleep_minutes')))
    low_days = sum(1 for s in s_qs if (s['avg'] or 9999) < 330)  # 330 min = 5.5h
    if low_days >= 3:
        highlights.append({
            "key": "low_sleep",
            "title": "Low Sleep",
            "detail": f"Average sleep < 5.5 hours on {low_days} day(s) this week.",
            "doctor_hint": False
        })

    # ---- Steps: today vs 30-day baseline; drop > 40%
    start30, end30 = _daterange(30)
    a_qs = (ActivityData.objects
            .filter(user=user, date__range=(start30, end30))
            .values('date')
            .annotate(avg_steps=Avg('steps')))
    if a_qs:
        # Compute baseline on the past 30 days excluding today (if present)
        today = date.today()
        steps_by_day = {row['date']: row['avg_steps'] or 0 for row in a_qs}
        today_steps = steps_by_day.get(today, 0)
        baseline_days = [v for d, v in steps_by_day.items() if d != today and v is not None]
        if baseline_days:
            baseline = sum(baseline_days) / len(baseline_days)
            if baseline > 0:
                drop = (baseline - today_steps) / baseline
                if drop > 0.40:  # > 40%
                    pct = int(round(drop * 100))
                    highlights.append({
                        "key": "activity_drop",
                        "title": "Activity Drop",
                        "detail": f"Today's steps are {pct}% below your 30-day average.",
                        "doctor_hint": False
                    })

    # Keep only up to 'limit'
    return highlights[:limit]
