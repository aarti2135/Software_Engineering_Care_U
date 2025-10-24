# healthdata/views.py

# ---------- DRF API ----------
from rest_framework import viewsets, permissions, status
from .models import NutritionEntry
from .serializers import NutritionEntrySerializer
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from .models import HealthReminder
from .serializers import HealthReminderSerializer
from .reminders_engine import ReminderEngine
from datetime import datetime, timedelta

class NutritionEntryViewSet(viewsets.ModelViewSet):
    """
    CRUD API for a user's own nutrition entries.
    """
    serializer_class = NutritionEntrySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return (
            NutritionEntry.objects
            .filter(user=self.request.user)
            .order_by("-logged_at", "-created_at")
        )

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


# ========== DRF API ViewSet ==========

class HealthReminderViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API ViewSet for health reminders.

    Endpoints:
    - GET /api/reminders/ - List active reminders
    - GET /api/reminders/{id}/ - Get specific reminder
    - POST /api/reminders/generate/ - Generate new reminders
    - POST /api/reminders/{id}/dismiss/ - Dismiss a reminder
    - POST /api/reminders/{id}/act_upon/ - Mark as acted upon
    """
    serializer_class = HealthReminderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Return only active reminders for current user."""
        return HealthReminder.objects.filter(
            user=self.request.user,
            dismissed_at__isnull=True
        ).order_by('-priority', '-created_at')

    @action(detail=False, methods=['post'])
    def generate(self, request):
        """
        Generate new reminders based on current health data.
        POST /api/reminders/generate/
        """
        engine = ReminderEngine(request.user)
        new_reminders = engine.analyze_and_create_reminders()

        serializer = self.get_serializer(new_reminders, many=True)
        return Response({
            'count': len(new_reminders),
            'reminders': serializer.data
        }, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def dismiss(self, request, pk=None):
        """
        Dismiss a reminder.
        POST /api/reminders/{id}/dismiss/
        """
        reminder = self.get_object()
        reminder.dismissed_at = timezone.now()
        reminder.save()

        return Response({
            'status': 'dismissed',
            'message': f'Reminder "{reminder.title}" dismissed successfully.'
        })

    @action(detail=True, methods=['post'])
    def act_upon(self, request, pk=None):
        """
        Mark reminder as acted upon.
        POST /api/reminders/{id}/act_upon/
        """
        reminder = self.get_object()
        reminder.acted_upon = True
        reminder.acted_upon_at = timezone.now()
        reminder.save()

        return Response({
            'status': 'acted_upon',
            'message': f'Great! You acted on "{reminder.title}".'
        })

# ---------- HTML Dashboard ----------
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.db.models import Sum
from .forms import NutritionEntryForm

@login_required
def nutrition_dashboard(request):
    """
    HTML dashboard to view and add Nutrition Entries (current user only).
    Provides today totals for calories/macros.
    """
    # create
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

    # list
    entries = (
        NutritionEntry.objects
        .filter(user=request.user)
        .order_by("-logged_at", "-created_at")
    )

    # today totals
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
        "protein":  agg["protein"] or 0,
        "carbs":    agg["carbs"] or 0,
        "fat":      agg["fat"] or 0,
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


@login_required
def nutrition_edit(request, pk: int):
    """
    Edit an existing entry owned by the current user.
    """
    entry = get_object_or_404(NutritionEntry, pk=pk, user=request.user)
    if request.method == "POST":
        form = NutritionEntryForm(request.POST, instance=entry)
        if form.is_valid():
            form.save()
            messages.success(request, "Nutrition entry updated.")
            return redirect("nutrition_dashboard")
    else:
        form = NutritionEntryForm(instance=entry)

    return render(
        request,
        "healthdata/nutrition_edit.html",
        {"form": form, "entry": entry},
    )


@login_required
def nutrition_delete(request, pk: int):
    """
    Confirm and delete an entry owned by the current user.
    """
    entry = get_object_or_404(NutritionEntry, pk=pk, user=request.user)
    if request.method == "POST":
        entry.delete()
        messages.success(request, "Nutrition entry deleted.")
        return redirect("nutrition_dashboard")

    return render(
        request,
        "healthdata/nutrition_confirm_delete.html",
        {"entry": entry},
    )


@login_required
def reminders_dashboard(request):
    """HTML dashboard to view health reminders."""
    # Generate new reminders
    engine = ReminderEngine(request.user)
    new_reminders = engine.analyze_and_create_reminders()

    if new_reminders:
        messages.info(request, f'{len(new_reminders)} new health insight(s) generated!')

    # Get active reminders
    priority_order = {'high': 0, 'medium': 1, 'low': 2}
    reminders = HealthReminder.objects.filter(
        user=request.user,
        dismissed_at__isnull=True
    )
    reminders = sorted(reminders, key=lambda r: priority_order.get(r.priority, 3))

    # Dismissed reminders
    dismissed_reminders = HealthReminder.objects.filter(
        user=request.user,
        dismissed_at__isnull=False
    ).order_by('-dismissed_at')[:5]

    # Calculate stats
    acted_upon_count = sum(1 for r in reminders if r.acted_upon)

    # Generate week days for header
    today = timezone.localdate()
    week_days = []
    for i in range(7):
        day = today - timedelta(days=today.weekday()) + timedelta(days=i)
        has_data = NutritionEntry.objects.filter(
            user=request.user,
            logged_at=day
        ).exists()

        week_days.append({
            'name': day.strftime('%a'),
            'date': day.day,
            'is_today': day == today,
            'has_data': has_data
        })

    return render(request, 'healthdata/reminders_dashboard.html', {
        'reminders': reminders,
        'dismissed_reminders': dismissed_reminders,
        'acted_upon_count': acted_upon_count,
        'week_days': week_days,  # ADD THIS
    })


@login_required
def dismiss_reminder(request, pk: int):
    """
    Dismiss a reminder (mark as no longer active).
    """
    reminder = get_object_or_404(HealthReminder, pk=pk, user=request.user)

    if request.method == 'POST':
        reminder.dismissed_at = timezone.now()
        reminder.save()
        messages.success(request, f'Reminder "{reminder.title}" dismissed.')
        return redirect('reminders_dashboard')

    # If GET, show confirmation page
    return render(request, 'healthdata/reminder_confirm_dismiss.html', {
        'reminder': reminder
    })


@login_required
def act_on_reminder(request, pk: int):
    """
    Mark a reminder as acted upon (user followed the advice).
    """
    reminder = get_object_or_404(HealthReminder, pk=pk, user=request.user)

    if request.method == 'POST':
        reminder.acted_upon = True
        reminder.acted_upon_at = timezone.now()
        # Also dismiss it since they acted on it
        reminder.dismissed_at = timezone.now()
        reminder.save()

        messages.success(request, f'Great job! You acted on "{reminder.title}".')
        return redirect('reminders_dashboard')

    return redirect('reminders_dashboard')
