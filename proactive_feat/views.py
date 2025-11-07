# proactive_feat/views.py

from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponseRedirect, HttpResponse
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django import forms
from django.utils.http import url_has_allowed_host_and_scheme  # for safe redirects

# where to go "back to dashboard"
DASHBOARD_URL = "/api/dashboard/reminders/"

from .models import VitalReading, Alert


# ---------- Forms ----------
class VitalForm(forms.ModelForm):
    class Meta:
        model = VitalReading
        fields = ["kind", "value", "measured_at"]


# ---------- Public (no auth) ----------
def ping(_request):
    # Simple health check for URL wiring
    return HttpResponse("pong")


# ---------- Auth-required views ----------
@login_required
def vital_form(request):
    if request.method == "POST":
        form = VitalForm(request.POST)
        if form.is_valid():
            vr = form.save(commit=False)
            vr.user = request.user
            vr.save()
            messages.success(request, "Vital saved.")

            # Prefer ?next= or posted next= if safe; else go to dashboard
            next_url = request.POST.get("next") or request.GET.get("next")
            if next_url and url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}):
                return HttpResponseRedirect(next_url)

            return HttpResponseRedirect(DASHBOARD_URL)
    else:
        form = VitalForm()

    # Pass DASHBOARD_URL so template can render a Back button
    return render(
        request,
        "proactive_feat/vitals_form.html",
        {"form": form, "DASHBOARD_URL": DASHBOARD_URL},
    )


@login_required
def alerts_list(request):
    alerts = Alert.objects.filter(user=request.user).order_by("-created_at")[:100]
    return render(
        request,
        "proactive_feat/alerts_list.html",
        {"alerts": alerts, "DASHBOARD_URL": DASHBOARD_URL},  # ensure available
    )


@login_required
def unread_alerts_json(request):
    alerts = (
        Alert.objects
        .filter(user=request.user, is_read=False, is_dismissed=False)
        .order_by("-created_at")[:10]
    )
    data = [
        {"id": a.id, "type": a.alert_type, "message": a.message, "ts": a.created_at.isoformat()}
        for a in alerts
    ]
    return JsonResponse({"alerts": data})


@login_required
def alert_mark_read(request, pk):
    a = get_object_or_404(Alert, pk=pk, user=request.user)
    a.is_read = True
    a.save()
    return JsonResponse({"ok": True})


@login_required
def launcher(request):
    return render(
        request,
        "proactive_feat/launcher.html",
        {"DASHBOARD_URL": DASHBOARD_URL},  # ensure available
    )
