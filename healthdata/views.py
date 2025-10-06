# healthdata/views.py

# ---------- DRF API ----------
from rest_framework import viewsets, permissions
from .models import NutritionEntry
from .serializers import NutritionEntrySerializer

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
