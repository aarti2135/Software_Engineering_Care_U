from datetime import datetime, timedelta
import csv
import io
import logging

# ---------- DRF ----------
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone

from .models import (
    NutritionEntry, HealthReminder,
    GlucoseEntry, MedicationEntry, DoctorNote,
    VitalLog, MoodLog, SymptomLog, HabitLog, WellbeingLog,
    Goal
)
from .serializers import (
    NutritionEntrySerializer, HealthReminderSerializer,
    GlucoseEntrySerializer, MedicationEntrySerializer, DoctorNoteSerializer,
    VitalLogSerializer, MoodLogSerializer, SymptomLogSerializer,
    HabitLogSerializer, WellbeingLogSerializer
)
from .forms import NutritionEntryForm, GoalForm
from .reminders_engine import ReminderEngine
from ai_agent.services import AIAgentService


logger = logging.getLogger(__name__)

# ----------------------------------------------------------------------
# 🔹 API ViewSets
# ----------------------------------------------------------------------
class NutritionEntryViewSet(viewsets.ModelViewSet):
    """CRUD API for user's nutrition entries."""
    serializer_class = NutritionEntrySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return NutritionEntry.objects.filter(
            user=self.request.user
        ).order_by("-logged_at", "-created_at")

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class HealthReminderViewSet(viewsets.ReadOnlyModelViewSet):
    """Read-only API for user health reminders."""
    serializer_class = HealthReminderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return HealthReminder.objects.filter(
            user=self.request.user,
            dismissed_at__isnull=True
        ).order_by('-priority', '-created_at')

    @action(detail=False, methods=['post'])
    def generate(self, request):
        engine = ReminderEngine(request.user)
        new_reminders = engine.analyze_and_create_reminders()
        serializer = self.get_serializer(new_reminders, many=True)
        return Response({
            'count': len(new_reminders),
            'reminders': serializer.data
        }, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def dismiss(self, request, pk=None):
        reminder = self.get_object()
        reminder.dismissed_at = timezone.now()
        reminder.save()
        return Response({'status': 'dismissed'})

    @action(detail=True, methods=['post'])
    def act_upon(self, request, pk=None):
        reminder = self.get_object()
        reminder.acted_upon = True
        reminder.acted_upon_at = timezone.now()
        reminder.save()
        return Response({'status': 'acted_upon'})


# ----------------------------------------------------------------------
# 🔹 HTML Views
# ----------------------------------------------------------------------
@login_required
def home_dashboard(request):
    """Main landing page after login → uses proactive dashboard."""
    return render(request, "proactive_feat/home_dashboard.html")


# ----------------------------------------------------------------------
# 🔹 Nutrition Dashboard
# ----------------------------------------------------------------------
@login_required
def nutrition_dashboard(request):
    """Nutrition Dashboard (add / view entries + import CSV)."""
    if request.method == "POST":
        form = NutritionEntryForm(request.POST)
        if form.is_valid():
            entry = form.save(commit=False)
            entry.user = request.user
            entry.save()
            messages.success(request, "Nutrition entry added successfully!")
            return redirect("nutrition_dashboard")
    else:
        form = NutritionEntryForm()

    entries = NutritionEntry.objects.filter(
        user=request.user
    ).order_by("-logged_at", "-created_at")

    today = timezone.localdate()
    today_qs = NutritionEntry.objects.filter(user=request.user, logged_at=today)
    agg = today_qs.aggregate(
        calories=Sum("calories"),
        protein=Sum("protein_g"),
        carbs=Sum("carbs_g"),
        fat=Sum("fat_g"),
    )
    today_totals = {
        "calories": agg["calories"] or 0,
        "protein": agg["protein"] or 0,
        "carbs": agg["carbs"] or 0,
        "fat": agg["fat"] or 0,
    }

    return render(
        request,
        "healthdata/nutrition_dashboard.html",
        {
            "form": form,
            "entries": entries,
            "today": today,
            "today_totals": today_totals,
        },
    )


# ----------------------------------------------------------------------
# 🔹 CSV Import (robust)
# ----------------------------------------------------------------------
@login_required
def nutrition_import(request):
    """
    Import nutrition data from CSV (auto-detect delimiter and date format).
    Expected columns:
      logged_at, meal_type, calories, protein_g, carbs_g, fat_g, notes
    """
    if request.method == "POST" and request.FILES.get("csv_file"):
        file = request.FILES["csv_file"]
        try:
            decoded = file.read().decode("utf-8").strip()
            first_line = decoded.splitlines()[0]
            delimiter = ";" if ";" in first_line else ("\t" if "\t" in first_line else ",")
            reader = csv.DictReader(io.StringIO(decoded), delimiter=delimiter)

            created_count, skipped_count = 0, 0

            for row in reader:
                if not any(row.values()):
                    skipped_count += 1
                    continue

                logged_at_raw = (row.get("logged_at") or "").strip()
                if not logged_at_raw:
                    skipped_count += 1
                    continue

                logged_at = None
                for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%Y/%m/%d", "%m/%d/%Y"):
                    try:
                        logged_at = datetime.strptime(logged_at_raw, fmt).date()
                        break
                    except ValueError:
                        continue

                if not logged_at:
                    skipped_count += 1
                    continue

                try:
                    NutritionEntry.objects.create(
                        user=request.user,
                        logged_at=logged_at,
                        meal_type=row.get("meal_type", "").strip() or "Unknown",
                        calories=float(row.get("calories") or 0),
                        protein_g=float(row.get("protein_g") or 0),
                        carbs_g=float(row.get("carbs_g") or 0),
                        fat_g=float(row.get("fat_g") or 0),
                        notes=row.get("notes", "").strip(),
                    )
                    created_count += 1
                except Exception:
                    skipped_count += 1

            msg = f"✅ Successfully imported {created_count} entries."
            if skipped_count:
                msg += f" ({skipped_count} row(s) skipped due to invalid data.)"
            messages.success(request, msg)

        except Exception as e:
            messages.error(request, f"⚠️ Error importing CSV: {e}")

    return redirect("nutrition_dashboard")


# ----------------------------------------------------------------------
# 🔹 Edit / Delete Nutrition Entries
# ----------------------------------------------------------------------
@login_required
def nutrition_edit(request, pk):
    entry = get_object_or_404(NutritionEntry, pk=pk, user=request.user)
    if request.method == "POST":
        form = NutritionEntryForm(request.POST, instance=entry)
        if form.is_valid():
            form.save()
            messages.success(request, "Nutrition entry updated.")
            return redirect("nutrition_dashboard")
    else:
        form = NutritionEntryForm(instance=entry)
    return render(request, "healthdata/nutrition_edit.html", {"form": form, "entry": entry})


@login_required
def nutrition_delete(request, pk):
    entry = get_object_or_404(NutritionEntry, pk=pk, user=request.user)
    if request.method == "POST":
        entry.delete()
        messages.success(request, "Nutrition entry deleted.")
        return redirect("nutrition_dashboard")
    return render(request, "healthdata/nutrition_confirm_delete.html", {"entry": entry})


# ----------------------------------------------------------------------
# 🔹 Goals Management
# ----------------------------------------------------------------------
@login_required
def goal_dashboard(request):
    """Display all user goals with progress overview."""
    goals = Goal.objects.filter(user=request.user).order_by("-created_at")
    return render(request, "healthdata/goal_dashboard.html", {"goals": goals})


@login_required
def goal_create(request):
    """Create a new goal."""
    if request.method == "POST":
        form = GoalForm(request.POST)
        if form.is_valid():
            goal = form.save(commit=False)
            goal.user = request.user
            goal.save()
            messages.success(request, "🎯 Goal created successfully!")
            return redirect("goal_dashboard")
    else:
        form = GoalForm()
    return render(request, "healthdata/goal_form.html", {"form": form, "action": "Create"})


@login_required
def goal_edit(request, pk):
    """Edit an existing goal."""
    goal = get_object_or_404(Goal, pk=pk, user=request.user)
    if request.method == "POST":
        form = GoalForm(request.POST, instance=goal)
        if form.is_valid():
            form.save()
            messages.success(request, "Goal updated successfully!")
            return redirect("goal_dashboard")
    else:
        form = GoalForm(instance=goal)
    return render(request, "healthdata/goal_form.html", {"form": form, "action": "Edit", "goal": goal})


@login_required
def goal_delete(request, pk):
    """Delete a goal."""
    goal = get_object_or_404(Goal, pk=pk, user=request.user)
    if request.method == "POST":
        goal.delete()
        messages.success(request, "Goal deleted.")
        return redirect("goal_dashboard")
    return render(request, "healthdata/goal_confirm_delete.html", {"goal": goal})


# ----------------------------------------------------------------------
# 🔹 Reminder Dashboards
# ----------------------------------------------------------------------
@login_required
def reminders_dashboard(request):
    engine = ReminderEngine(request.user)
    new_reminders = engine.analyze_and_create_reminders()
    if new_reminders:
        messages.info(request, f'{len(new_reminders)} new health insight(s) generated!')

    priority_order = {'high': 0, 'medium': 1, 'low': 2}
    reminders = sorted(
        HealthReminder.objects.filter(user=request.user, dismissed_at__isnull=True),
        key=lambda r: priority_order.get(r.priority, 3)
    )
    dismissed_reminders = HealthReminder.objects.filter(
        user=request.user, dismissed_at__isnull=False
    ).order_by('-dismissed_at')[:5]

    today = timezone.localdate()
    week_days = []
    for i in range(7):
        day = today - timedelta(days=today.weekday()) + timedelta(days=i)
        has_data = NutritionEntry.objects.filter(user=request.user, logged_at=day).exists()
        week_days.append({
            'name': day.strftime('%a'),
            'date': day.day,
            'is_today': day == today,
            'has_data': has_data,
        })

    # ------------------------------------------------------------------
    # 🔹 AI Insight (short motivational text based on current reminders)
    # ------------------------------------------------------------------
    daily_ai_insight = None
    try:
        # Only try to generate an insight if there are active reminders
        if reminders:
            agent_service = AIAgentService(request.user)
            result = agent_service.process_message(
                message=(
                    "Give 1-2 very short, friendly sentences encouraging the user "
                    "based on their current health reminders. Focus on positive, "
                    "non-medical guidance (e.g., consistency with logging, balanced "
                    "nutrition, staying active, hydration, and sleep). Keep it brief."
                ),
                days_to_analyze=7,
            )
            if not result.get("error") and result.get("response"):
                # Trim to a short length for the sidebar (approx. 1-2 lines)
                daily_ai_insight = result["response"].strip()[:160]
    except Exception as e:
        # Log but don't break the page if AI insight fails
        logger.warning(f"Failed to generate daily AI insight: {e}")

    return render(request, "healthdata/reminders_dashboard.html", {
        "reminders": reminders,
        "dismissed_reminders": dismissed_reminders,
        "acted_upon_count": sum(1 for r in reminders if r.acted_upon),
        "week_days": week_days,
        "daily_ai_insight": daily_ai_insight,
    })


@login_required
def dismiss_reminder(request, pk):
    reminder = get_object_or_404(HealthReminder, pk=pk, user=request.user)
    if request.method == "POST":
        reminder.dismissed_at = timezone.now()
        reminder.save()
        messages.success(request, f'Reminder "{reminder.title}" dismissed.')
        return redirect("reminders_dashboard")
    return render(request, "healthdata/reminder_confirm_dismiss.html", {"reminder": reminder})


@login_required
def act_on_reminder(request, pk):
    reminder = get_object_or_404(HealthReminder, pk=pk, user=request.user)
    if request.method == "POST":
        reminder.acted_upon = True
        reminder.acted_upon_at = timezone.now()
        reminder.dismissed_at = timezone.now()
        reminder.save()
        messages.success(request, f'Great job! You acted on "{reminder.title}".')
        return redirect("reminders_dashboard")
    return redirect("reminders_dashboard")


# ----------------------------------------------------------------------
# 🔹 Other Models (Healthlog API)
# ----------------------------------------------------------------------
class GlucoseEntryViewSet(viewsets.ModelViewSet):
    serializer_class = GlucoseEntrySerializer
    permission_classes = [permissions.IsAuthenticated]
    def get_queryset(self):
        return GlucoseEntry.objects.filter(user=self.request.user).order_by("-created_at")
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class MedicationEntryViewSet(viewsets.ModelViewSet):
    serializer_class = MedicationEntrySerializer
    permission_classes = [permissions.IsAuthenticated]
    def get_queryset(self):
        return MedicationEntry.objects.filter(user=self.request.user).order_by("-time_taken", "-created_at")
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class DoctorNoteViewSet(viewsets.ModelViewSet):
    serializer_class = DoctorNoteSerializer
    permission_classes = [permissions.IsAuthenticated]
    def get_queryset(self):
        return DoctorNote.objects.filter(user=self.request.user).order_by("-created_at")
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class VitalLogViewSet(viewsets.ModelViewSet):
    serializer_class = VitalLogSerializer
    permission_classes = [permissions.IsAuthenticated]
    def get_queryset(self):
        return VitalLog.objects.filter(user=self.request.user).order_by("-created_at")
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class MoodLogViewSet(viewsets.ModelViewSet):
    serializer_class = MoodLogSerializer
    permission_classes = [permissions.IsAuthenticated]
    def get_queryset(self):
        return MoodLog.objects.filter(user=self.request.user).order_by("-created_at")
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class SymptomLogViewSet(viewsets.ModelViewSet):
    serializer_class = SymptomLogSerializer
    permission_classes = [permissions.IsAuthenticated]
    def get_queryset(self):
        return SymptomLog.objects.filter(user=self.request.user).order_by("-created_at")
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class HabitLogViewSet(viewsets.ModelViewSet):
    serializer_class = HabitLogSerializer
    permission_classes = [permissions.IsAuthenticated]
    def get_queryset(self):
        return HabitLog.objects.filter(user=self.request.user).order_by("-date", "-created_at")
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class WellbeingLogViewSet(viewsets.ModelViewSet):
    serializer_class = WellbeingLogSerializer
    permission_classes = [permissions.IsAuthenticated]
    def get_queryset(self):
        return WellbeingLog.objects.filter(user=self.request.user).order_by("-date", "-created_at")
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


# ----------------------------------------------------------------------
# 🔹 Utility Redirect
# ----------------------------------------------------------------------
def redirect_to_home_dashboard(request):
    return redirect("home_dashboard")
