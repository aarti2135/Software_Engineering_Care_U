from datetime import date, timedelta, datetime
import random

from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model
from django.apps import apps
from django.db import transaction
from django.db.models import (
    DateField, DateTimeField, IntegerField, FloatField, DecimalField, Field
)

User = get_user_model()

# ---------- Field helpers ----------

def field_map(Model):
    return {f.name: f for f in Model._meta.get_fields() if isinstance(f, Field)}

def is_dt_field(f):
    return isinstance(f, (DateTimeField,))

def is_date_field(f):
    return isinstance(f, (DateField,))

def is_numeric_field(f):
    return isinstance(f, (IntegerField, FloatField, DecimalField))

def pick_by_name(name: str, keywords):
    name_lc = (name or "").lower()
    return any(kw in name_lc for kw in keywords)

def pick_best_date_field(Model, preferred=("date","created_at","recorded_at","timestamp","logged_at")):
    fm = field_map(Model)
    # 1) preferred names (date or datetime)
    for p in preferred:
        if p in fm and (is_date_field(fm[p]) or is_dt_field(fm[p])):
            return p, is_dt_field(fm[p])
    # 2) any date/datetime field
    for n, f in fm.items():
        if is_date_field(f) or is_dt_field(f):
            return n, is_dt_field(f)
    return None, None

def pick_best_numeric_field(Model, preferred_keywords=("sleep","hour","minute","duration","glucose","step","count","value")):
    fm = field_map(Model)
    # 1) numeric field whose name contains preferred keywords
    for n, f in fm.items():
        if is_numeric_field(f) and pick_by_name(n, preferred_keywords):
            return n
    # 2) any numeric field except common foreign keys/ids
    for n, f in fm.items():
        if is_numeric_field(f) and n not in ("id","user_id"):
            return n
    return None

def date_filter_kwargs(date_field, start, end, is_datetime):
    if is_datetime:
        return {f"{date_field}__date__gte": start, f"{date_field}__date__lte": end}
    return {f"{date_field}__gte": start, f"{date_field}__lte": end}

def set_date_value(is_datetime, d):
    return datetime.combine(d, datetime.min.time()).replace(hour=12) if is_datetime else d

def is_minutes_field(field_name: str) -> bool:
    n = (field_name or "").lower()
    return "minute" in n or n.endswith("_min") or n.endswith("_mins")

def is_hours_field(field_name: str) -> bool:
    n = (field_name or "").lower()
    return "hour" in n or n.endswith("_hr") or n.endswith("_hrs")


class Command(BaseCommand):
    help = "Seed realistic demo health data (glucose, sleep, steps) for Analytics."

    def add_arguments(self, parser):
        parser.add_argument("--username", help="Seed for this username (defaults to first active user).")
        parser.add_argument("--days", type=int, default=20, help="How many past days to seed (default: 20).")
        parser.add_argument("--reset", action="store_true", help="Delete existing rows in the range before seeding.")

    @transaction.atomic
    def handle(self, *args, **opts):
        # ---- Resolve user ----
        if opts.get("username"):
            user = User.objects.filter(username=opts["username"]).first()
            if not user:
                raise CommandError(f"User '{opts['username']}' not found.")
        else:
            user = User.objects.filter(is_active=True).order_by("id").first()
            if not user:
                raise CommandError("No active users found. Create one with 'python manage.py createsuperuser'.")

        days = max(7, int(opts.get("days", 20)))
        today = date.today()
        start = today - timedelta(days=days)

        # ---- Get your real models ----
        GlucoseEntry = apps.get_model("healthdata", "GlucoseEntry")
        SleepData    = apps.get_model("healthdata", "SleepData")
        ActivityData = apps.get_model("healthdata", "ActivityData")

        # ---- Resolve fields dynamically (with diagnostics) ----
        g_date, g_isdt = pick_best_date_field(GlucoseEntry)
        g_value = pick_best_numeric_field(GlucoseEntry, preferred_keywords=("glucose","mg","dl","value","reading"))
        s_date, s_isdt = pick_best_date_field(SleepData)
        s_value = pick_best_numeric_field(SleepData,    preferred_keywords=("total_sleep","sleep","minute","hour","duration","value"))
        a_date, a_isdt = pick_best_date_field(ActivityData)
        a_value = pick_best_numeric_field(ActivityData, preferred_keywords=("step","count","value"))

        diag = [
            f"GlucoseEntry: date_field={g_date!r} ({'DateTime' if g_isdt else 'Date'}) value_field={g_value!r}",
            f"SleepData   : date_field={s_date!r} ({'DateTime' if s_isdt else 'Date'}) value_field={s_value!r}",
            f"ActivityData: date_field={a_date!r} ({'DateTime' if a_isdt else 'Date'}) value_field={a_value!r}",
        ]
        self.stdout.write("\n".join(diag))

        if not (g_date and g_value):
            fm = ", ".join(field_map(GlucoseEntry).keys())
            raise CommandError(f"Could not resolve fields on GlucoseEntry. Fields: {fm}")
        if not (s_date and s_value):
            fm = ", ".join(field_map(SleepData).keys())
            raise CommandError(f"Could not resolve fields on SleepData. Fields: {fm}")
        if not (a_date and a_value):
            fm = ", ".join(field_map(ActivityData).keys())
            raise CommandError(f"Could not resolve fields on ActivityData. Fields: {fm}")

        # Determine sleep units based on field name
        sleep_as_minutes = True
        if is_hours_field(s_value):
            sleep_as_minutes = False
        elif is_minutes_field(s_value):
            sleep_as_minutes = True
        else:
            # default to minutes (most models store minutes)
            sleep_as_minutes = True

        # ---- Optional reset ----
        if opts.get("reset"):
            GlucoseEntry.objects.filter(user=user, **date_filter_kwargs(g_date, start, today, g_isdt)).delete()
            SleepData.objects.filter(user=user, **date_filter_kwargs(s_date, start, today, s_isdt)).delete()
            ActivityData.objects.filter(user=user, **date_filter_kwargs(a_date, start, today, a_isdt)).delete()

        # ---- Seed baseline steps (older part of window) ----
        for i in range(days, 6, -1):  # older days baseline
            d = today - timedelta(days=i)
            ActivityData.objects.update_or_create(
                user=user,
                **{a_date: set_date_value(a_isdt, d)},
                defaults={a_value: random.randint(9000, 11500)},
            )

        # ---- Seed main window ----
        for i in range(days, 0, -1):
            d = today - timedelta(days=i)

            # Glucose: typical range 95–130 mg/dL
            GlucoseEntry.objects.update_or_create(
                user=user,
                **{g_date: set_date_value(g_isdt, d)},
                defaults={g_value: random.randint(95, 130)},
            )

            # Sleep: realistic values
            if sleep_as_minutes:
                # minutes: 6.2–7.6 hours
                sleep_val = random.randint(372, 456)  # 6.2h–7.6h in minutes
            else:
                # hours (to one decimal)
                sleep_val = round(random.uniform(6.2, 7.6), 1)

            SleepData.objects.update_or_create(
                user=user,
                **{s_date: set_date_value(s_isdt, d)},
                defaults={s_value: sleep_val},
            )

            # Steps: typical 7k–11k
            ActivityData.objects.update_or_create(
                user=user,
                **{a_date: set_date_value(a_isdt, d)},
                defaults={a_value: random.randint(7000, 11000)},
            )

        # ---- Triggers (your acceptance criteria) ----
        # High Glucose: last 2 days high (190–220 mg/dL)
        for i in (2, 1):
            d = today - timedelta(days=i)
            GlucoseEntry.objects.update_or_create(
                user=user,
                **{g_date: set_date_value(g_isdt, d)},
                defaults={g_value: random.randint(190, 220)},
            )

        # Low Sleep: 3 days below 5.5h
        for i in (5, 4, 3):
            d = today - timedelta(days=i)
            if sleep_as_minutes:
                low_sleep_val = random.randint(252, 330)  # 4.2h–5.5h in minutes
            else:
                low_sleep_val = round(random.uniform(4.2, 5.3), 1)
            SleepData.objects.update_or_create(
                user=user,
                **{s_date: set_date_value(s_isdt, d)},
                defaults={s_value: low_sleep_val},
            )

        # Activity Drop: last 3 days low steps
        for i in (3, 2, 1):
            d = today - timedelta(days=i)
            ActivityData.objects.update_or_create(
                user=user,
                **{a_date: set_date_value(a_isdt, d)},
                defaults={a_value: random.randint(3000, 4500)},
            )

        self.stdout.write(self.style.SUCCESS(
            f"✅ Seeded {days} days for '{user.username}'. Open the Analytics panel to see charts & highlights."
        ))