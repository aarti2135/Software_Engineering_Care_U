from datetime import timedelta
from django.utils import timezone

# Default thresholds (can be moved to per-user settings later)
DEFAULT_THRESHOLDS = {
    "glucose": {"high": 180, "low": 70},
    "bp_sys":  {"high": 140, "low": 90},
    "bp_dia":  {"high": 90,  "low": 60},
    "hr":      {"high": 120, "low": 50},
    "spo2":    {"low": 94},
    "temp":    {"high": 38.0, "low": 35.0},
}

def evaluate_threshold(kind: str, value: float):
    t = DEFAULT_THRESHOLDS.get(kind, {})
    if "high" in t and value > t["high"]:
        return f"{kind} high ({value})"
    if "low" in t and value < t["low"]:
        return f"{kind} low ({value})"
    return None

def last_log_older_than(qs, hours=24):
    last = qs.order_by("-measured_at").first()
    if not last:
        return True
    return timezone.now() - last.measured_at > timedelta(hours=hours)
