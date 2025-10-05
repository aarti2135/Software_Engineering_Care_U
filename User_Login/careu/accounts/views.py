from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .forms import SignUpForm
from django.contrib.auth import logout
from django.http import HttpResponseNotAllowed
from .models import Profile
from django.shortcuts import redirect


def register(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Save extra fields into Profile
            dob = form.cleaned_data.get('date_of_birth')
            Profile.objects.create(user=user, date_of_birth=dob)
            login(request, user)
            return redirect("dashboard")
    else:
        form = SignUpForm()
    return render(request, "accounts/register.html", {"form": form})

@login_required
def dashboard(request):
    return render(request, "accounts/dashboard.html")

def logout_view(request):
    # Allow both GET and POST for now (dev-friendly)
    if request.method in ("GET", "POST"):
        logout(request)
        return redirect("login")
    return HttpResponseNotAllowed(["GET", "POST"])
