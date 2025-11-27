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
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone

from .models import (
    NutritionEntry, HealthReminder,
    GlucoseEntry, MedicationEntry, DoctorNote,
    VitalLog, MoodLog, SymptomLog, HabitLog, WellbeingLog,
    Goal, ActivityData, HealthMetrics
)
from .serializers import (
    NutritionEntrySerializer, HealthReminderSerializer,
    GlucoseEntrySerializer, MedicationEntrySerializer, DoctorNoteSerializer,
    VitalLogSerializer, MoodLogSerializer, SymptomLogSerializer,
    HabitLogSerializer, WellbeingLogSerializer
)
from .forms import NutritionEntryForm, GoalForm
from .reminders_engine import ReminderEngine
from ai_agent.services import AIAgentService, SAFETY_DISCLAIMER
from healthdata.export_service import HealthReportGenerator
from healthdata.transparency import TransparencyLabel

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
    """Main landing page after login with health metrics."""
    from gamification.services import GamificationService
    from gamification.models import UserBadge, Badge

    user = request.user
    today = timezone.localdate()

    # 1️⃣ Get today's steps
    today_activity = ActivityData.objects.filter(user=user, date=today).first()
    steps_today = today_activity.steps if today_activity else 0

    # 2️⃣ Get latest heart rate
    latest_heart_rate_entry = HealthMetrics.objects.filter(
        user=user,
        heart_rate_resting__isnull=False
    ).order_by('-logged_at').first()
    heart_rate = latest_heart_rate_entry.heart_rate_resting if latest_heart_rate_entry else 0

    # 3️⃣ Get latest active goal
    latest_goal = Goal.objects.filter(user=user, status='active').order_by('-created_at').first()

    goal = None
    if latest_goal:
        goal = {
            "title": latest_goal.title or f"{latest_goal.get_goal_type_display()} Goal",
            "notes": latest_goal.notes or f"Target: {latest_goal.target_value}",
        }

    # Initialize gamification defaults
    current_streak = 0
    longest_streak = 0
    total_activities = 0
    badges_earned = 0
    total_badges = 6
    weekly_percentage = 0
    weekly_days_completed = 0
    weekly_goal_target = 7
    badges_data = []

    # 4️⃣ Get gamification stats
    try:
        gamification_service = GamificationService(user)
        gamification_stats = gamification_service.get_user_stats()

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

    except Exception as e:
        logger.warning(f"Gamification error: {e}")

    # 5️⃣ Get user's avatar (MOVED OUTSIDE try-except block)
    try:
        from motivation.models import UserProfile
        profile = UserProfile.objects.get(user=user)
        current_avatar = profile.avatar
    except UserProfile.DoesNotExist:
        current_avatar = None

    # Build context data
    context = {
        'steps': steps_today,
        'heart_rate': heart_rate,
        'goal': goal,
        'today': today,
        'current_streak': current_streak,
        'longest_streak': longest_streak,
        'total_activities': total_activities,
        'badges_earned': badges_earned,
        'total_badges': total_badges,
        'weekly_percentage': weekly_percentage,
        'weekly_days_completed': weekly_days_completed,
        'weekly_goal_target': weekly_goal_target,
        'badges_data': badges_data,
        'current_avatar': current_avatar,  # Add avatar to context
    }

    return render(request, "proactive_feat/home_dashboard.html", context)
    # Build context data
    context = {
        'steps': steps_today,
        'heart_rate': heart_rate,
        'goal': goal,
        'today': today,
        'current_streak': current_streak,
        'longest_streak': longest_streak,
        'total_activities': total_activities,
        'badges_earned': badges_earned,
        'total_badges': total_badges,
        'weekly_percentage': weekly_percentage,
        'weekly_days_completed': weekly_days_completed,
        'weekly_goal_target': weekly_goal_target,
        'badges_data': badges_data,
        #'current_avatar': getattr(user, 'selected_avatar', None),  # Add this line
    }

    return render(request, "proactive_feat/home_dashboard.html", context)
# ----------------------------------------------------------------------
# 🔹 Nutrition Dashboard with Week View Navigation
# ----------------------------------------------------------------------
@login_required
def nutrition_dashboard(request):
    """Nutrition Dashboard with day-by-day filtering."""

    # Handle form submission for adding new entry
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

    # Get selected date from query parameter or default to today
    today = timezone.localdate()
    selected_date_str = request.GET.get('date')

    if selected_date_str:
        try:
            selected_date = datetime.strptime(selected_date_str, '%Y-%m-%d').date()
        except ValueError:
            selected_date = today
    else:
        selected_date = today

    # Calculate week boundaries (Monday to Sunday)
    week_start = selected_date - timedelta(days=selected_date.weekday())  # Monday
    week_end = week_start + timedelta(days=6)  # Sunday

    # Generate week days for navigation
    week_days = []
    for i in range(7):
        day = week_start + timedelta(days=i)
        has_data = NutritionEntry.objects.filter(
            user=request.user,
            logged_at=day
        ).exists()

        week_days.append({
            'date': day,
            'day_name': day.strftime('%a'),  # Mon, Tue, Wed...
            'day_number': day.day,
            'is_today': day == today,
            'is_selected': day == selected_date,
            'has_data': has_data,
        })

    # Calculate previous and next week dates
    prev_week_date = week_start - timedelta(days=7)
    next_week_date = week_start + timedelta(days=7)

    # Get entries for SELECTED DAY only
    entries = NutritionEntry.objects.filter(
        user=request.user,
        logged_at=selected_date
    ).order_by("-created_at")

    # Calculate totals for SELECTED DAY
    day_agg = NutritionEntry.objects.filter(
        user=request.user,
        logged_at=selected_date
    ).aggregate(
        calories=Sum("calories"),
        protein=Sum("protein_g"),
        carbs=Sum("carbs_g"),
        fat=Sum("fat_g"),
    )

    day_totals = {
        "calories": day_agg["calories"] or 0,
        "protein": float(day_agg["protein"] or 0),
        "carbs": float(day_agg["carbs"] or 0),
        "fat": float(day_agg["fat"] or 0),
    }

    return render(
        request,
        "healthdata/nutrition_dashboard.html",
        {
            "form": form,
            "entries": entries,
            "selected_date": selected_date,
            "today": today,
            "day_totals": day_totals,
            "week_days": week_days,
            "prev_week_date": prev_week_date,
            "next_week_date": next_week_date,
            "week_start": week_start,
            "week_end": week_end,
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
                # Use the full AI insight but strip the safety disclaimer for this sidebar box
                text = result["response"].strip()
                if SAFETY_DISCLAIMER in text:
                    text = text.replace(SAFETY_DISCLAIMER, "").strip()
                daily_ai_insight = text
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
        return MedicationEntry.objects.filter(
            user=self.request.user
        ).order_by("-time_taken", "-created_at")

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
        return HabitLog.objects.filter(
            user=self.request.user
        ).order_by("-date", "-created_at")

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class WellbeingLogViewSet(viewsets.ModelViewSet):
    serializer_class = WellbeingLogSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return WellbeingLog.objects.filter(
            user=self.request.user
        ).order_by("-date", "-created_at")

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


# ----------------------------------------------------------------------
# 🔹 Utility Redirect
# ----------------------------------------------------------------------
def redirect_to_home_dashboard(request):
    return redirect("home_dashboard")


# ----------------------------------------------------------------------
# 🔹 Epic 7 Story 2: Doctor Discussion Topics
# ----------------------------------------------------------------------
@login_required
def generate_doctor_discussion(request):
    """
    Generate AI-powered doctor discussion topics using existing AI agent.
    Integrates with Epic 7 Story 1 AI infrastructure.

    Returns JSON with observations, questions, context, and disclaimer.
    """
    if request.method != 'POST':
        return JsonResponse({
            'success': False,
            'error': 'Only POST requests are allowed'
        }, status=405)

    try:
        # Check if user has sufficient health data
        end_date = timezone.localdate()
        start_date = end_date - timedelta(days=30)

        # Count entries by type
        nutrition_count = NutritionEntry.objects.filter(
            user=request.user,
            logged_at__gte=start_date
        ).count()

        total_entries = nutrition_count

        if total_entries < 3:
            return JsonResponse({
                'success': False,
                'error': 'Insufficient health data. Please log at least 3 days of data before generating discussion topics.'
            }, status=400)

        # Initialize AI agent service (from Epic 7 Story 1)
        agent_service = AIAgentService(request.user)

        # Create specialized prompt for doctor discussion topics
        prompt = """I need help preparing for my doctor appointment. Based on my health data from the past 30 days, please generate a structured report with:

1. **Observations**: 3-5 key patterns or insights from my logged health data (nutrition, activity, sleep if available)
2. **Questions to Ask**: 3-5 specific questions I should discuss with my doctor based on my data
3. **Context**: 2-3 pieces of additional relevant information about my health behavior

**Important Guidelines:**
- Base everything on my actual logged data
- DO NOT provide medical advice or diagnoses
- Focus on observations and questions, not recommendations
- Be specific and reference actual data points when possible
- Keep each point concise (1-2 sentences)

Please structure your response clearly with these three sections."""

        # Call existing AI agent
        result = agent_service.process_message(
            message=prompt,
            days_to_analyze=30
        )

        # Check for errors
        if result.get('error'):
            logger.error(f"AI agent error for user {request.user.id}: {result['error']}")
            return JsonResponse({
                'success': False,
                'error': 'Unable to generate discussion topics. Please try again later.'
            }, status=500)

        # Parse the agent's response
        response_text = result.get('response', '')

        if not response_text:
            return JsonResponse({
                'success': False,
                'error': 'AI service returned an empty response. Please try again.'
            }, status=500)

        # Parse response into structured format
        topics = _parse_discussion_response(response_text)

        return JsonResponse({
            'success': True,
            'topics': topics
        })

    except Exception as e:
        logger.error(f"Error generating doctor discussion topics: {str(e)}", exc_info=True)
        return JsonResponse({
            'success': False,
            'error': 'An unexpected error occurred. Please try again later.'
        }, status=500)


def _parse_discussion_response(response_text):
    """
    Parse AI agent's response into structured format.

    Args:
        response_text: Raw text response from AI agent

    Returns:
        dict: Structured topics with observations, questions, context, disclaimer
    """
    # Remove safety disclaimer if present (we'll add our own)
    if SAFETY_DISCLAIMER in response_text:
        response_text = response_text.replace(SAFETY_DISCLAIMER, '').strip()

    topics = {
        'observations': [],
        'questions': [],
        'context': [],
        'disclaimer': 'These are observations from your data, not medical advice. Please discuss these topics with your healthcare provider.'
    }

    try:
        # Split response into lines
        lines = response_text.split('\n')
        current_section = None

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Detect section headers (case-insensitive)
            line_lower = line.lower()

            # Check for section headers
            if 'observation' in line_lower and len(line) < 100:
                current_section = 'observations'
                continue
            elif 'question' in line_lower and len(line) < 100:
                current_section = 'questions'
                continue
            elif 'context' in line_lower and len(line) < 100:
                current_section = 'context'
                continue

            # Skip lines that are too short or just formatting
            if len(line) < 10 or line in ['**', '---', '===']:
                continue

            # Clean up the line (remove bullets, numbers, asterisks)
            cleaned = line.replace('**', '').replace('*', '').strip()
            cleaned = cleaned.lstrip('0123456789.-–• ').strip()

            # Add to appropriate section
            if current_section and cleaned and len(cleaned) > 15:
                topics[current_section].append(cleaned)

        # If parsing didn't work well, try a simpler approach
        if not any(topics[key] for key in ['observations', 'questions', 'context']):
            # Just split into sentences and distribute
            sentences = [s.strip() for s in response_text.split('.') if len(s.strip()) > 20]

            # Distribute sentences across sections
            third = len(sentences) // 3
            topics['observations'] = sentences[:third] if third > 0 else sentences[:2]
            topics['questions'] = sentences[third:third * 2] if third > 0 else sentences[2:4]
            topics['context'] = sentences[third * 2:] if third > 0 else sentences[4:]

        # Ensure each section has at least one item
        if not topics['observations']:
            topics['observations'] = [
                'Based on your recent health data, there are patterns worth discussing with your doctor.']
        if not topics['questions']:
            topics['questions'] = ['What changes would you recommend based on my current health metrics?']
        if not topics['context']:
            topics['context'] = ['Your health data has been tracked consistently over the past month.']

    except Exception as e:
        logger.error(f"Error parsing discussion response: {str(e)}")
        # Return fallback structure
        topics['observations'] = ['Unable to parse AI response. Please try again.']

    return topics


# ----------------------------------------------------------------------
# 🔹 Export & Transparency Views
# ----------------------------------------------------------------------
@login_required
def export_dashboard(request):
    """Export dashboard page."""
    return render(request, 'healthdata/export_dashboard.html')


@login_required
def generate_health_report(request):
    """Generate PDF report."""
    try:
        days = int(request.GET.get('days', 30))
        days = max(7, min(days, 90))

        generator = HealthReportGenerator(request.user, days=days)
        pdf_buffer = generator.generate_pdf()

        response = HttpResponse(pdf_buffer, content_type='application/pdf')
        filename = f"CareU_Report_{request.user.username}_{datetime.now().strftime('%Y%m%d')}.pdf"
        response['Content-Disposition'] = f'attachment; filename="{filename}"'

        return response
    except Exception as e:
        return HttpResponse(f"Error: {str(e)}", status=500)


@login_required
def get_reminder_transparency(request, reminder_id):
    """Get transparency info for a reminder."""
    from healthdata.models import HealthReminder

    try:
        reminder = HealthReminder.objects.get(id=reminder_id, user=request.user)
        transparency_info = TransparencyLabel.get_label_for_reminder(reminder)

        return JsonResponse({
            'success': True,
            'reminder_id': reminder_id,
            'transparency': transparency_info
        })
    except HealthReminder.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Not found'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)
