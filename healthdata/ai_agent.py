# healthdata/ai_agent.py
from __future__ import annotations
from dataclasses import dataclass
from datetime import timedelta
from typing import Callable, List, Optional
from django.utils import timezone
from django.db import transaction
from django.contrib.auth import get_user_model

from healthdata.models import NutritionEntry
try:
    from healthdata.models import ActivityData, SleepData, HealthMetrics  # present in your repo after pull
except Exception:  # keep resilient if someone renames/removes a model
    ActivityData = None
    SleepData = None
    HealthMetrics = None

from usermanagement.models import ProviderAlert

User = get_user_model()


@dataclass
class RuleResult:
    triggered: bool
    alert_type: str
    severity: str          # "info" | "moderate" | "critical"
    message: str
    provider_hint: Optional[str] = None


@dataclass
class RiskRule:
    name: str
    evaluator: Callable[[User], RuleResult]
    enabled: bool = True


def _sustained_low_calories(user: User) -> RuleResult:
    qs = NutritionEntry.objects.filter(user=user).order_by("-logged_at")[:7]
    if not qs:
        return RuleResult(False, "", "", "")
    avg_cal = sum(e.calories for e in qs) / len(qs)
    if avg_cal < 1000:  # demo threshold; make configurable later
        return RuleResult(
            True,
            alert_type="Nutrition:LowIntake",
            severity="moderate",
            message="Calorie intake is consistently low over ~1 week.",
            provider_hint="Discuss nutrition sufficiency and fatigue/dehydration risks."
        )
    return RuleResult(False, "", "", "")


def _activity_drop(user: User) -> RuleResult:
    if ActivityData is None:
        return RuleResult(False, "", "", "")
    end = timezone.now().date()
    mid = end - timedelta(days=7)
    start = mid - timedelta(days=7)

    w2 = ActivityData.objects.filter(user=user, date__gt=mid, date__lte=end)
    w1 = ActivityData.objects.filter(user=user, date__gt=start, date__lte=mid)

    def total_steps(qs): return sum(getattr(a, "steps", 0) or 0 for a in qs)
    t1, t2 = total_steps(w1), total_steps(w2)
    if t1 > 0 and t2 < 0.6 * t1:
        return RuleResult(
            True,
            alert_type="Activity:SharpDrop",
            severity="moderate",
            message="Activity dropped >40% vs prior week.",
            provider_hint="Explore reasons (injury/illness/schedule). Consider gentle ramp-up."
        )
    return RuleResult(False, "", "", "")


def _sleep_insufficient(user: User) -> RuleResult:
    if SleepData is None:
        return RuleResult(False, "", "", "")
    last = list(SleepData.objects.filter(user=user).order_by("-date")[:5])
    if not last:
        return RuleResult(False, "", "", "")
    bad = sum(1 for s in last if (getattr(s, "duration_hours", 0) or 0) < 5)
    if bad >= 3:
        return RuleResult(
            True,
            alert_type="Sleep:Insufficient",
            severity="info",
            message="Frequent short sleep across recent nights.",
            provider_hint="Reinforce sleep hygiene; review stress/schedule factors."
        )
    return RuleResult(False, "", "", "")


RULES: List[RiskRule] = [
    RiskRule("Sustained Low Calories", _sustained_low_calories, enabled=True),
    RiskRule("Sharp Activity Drop", _activity_drop, enabled=True),
    RiskRule("Insufficient Sleep", _sleep_insufficient, enabled=True),
]


def _recent_duplicate_exists(user: User, alert_type: str, hours: int = 24) -> bool:
    cutoff = timezone.now() - timedelta(hours=hours)
    return ProviderAlert.objects.filter(
        user=user, alert_type=alert_type, created_at__gte=cutoff
    ).exists()


def evaluate_user(user: User) -> List[ProviderAlert]:
    """Run enabled rules for a user, consent-aware, suppress dupes, create ProviderAlert rows."""
    created: List[ProviderAlert] = []

    # Gate by consent on Profile (matches your current consent flow)
    try:
        if not bool(getattr(user.profile, "data_sharing_consent", False)):
            return created
    except Exception:
        # If profile missing in dev, don't block
        pass

    for rule in RULES:
        if not rule.enabled:
            continue
        res = rule.evaluator(user)
        if not res.triggered:
            continue
        if _recent_duplicate_exists(user, res.alert_type, hours=24):
            continue
        with transaction.atomic():
            hint = f"\n\nHint for provider: {res.provider_hint}" if getattr(res, "provider_hint", None) else ""
            alert = ProviderAlert.objects.create(
                user=user,
                alert_type=res.alert_type,
                message=f"{res.message}{hint}",
                severity=res.severity,  # 'low' | 'moderate' | 'high'
            )
            created.append(alert)
    return created
