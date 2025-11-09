# User_Login/views.py
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import logout
from usermanagement.forms import SignupForm


class UserLoginView(LoginView):
    """
    Displays the login form and logs the user in.
    After successful login → redirect to Home Dashboard (/dashboard/).
    If already authenticated → redirect directly to dashboard.
    """
    #  Use your correct template path
    template_name = "User_Login/login.html"

    #  Show login form even if user is already authenticated (so no auto redirect)
    redirect_authenticated_user = False

    #  Default redirect destination after login (if no ?next= param)
    success_url = reverse_lazy("dashboard")  # make sure 'dashboard' exists in healthdata/urls.py

    #  If ?next= is provided, Django handles it automatically; otherwise, fallback:
    def get_success_url(self):
        return self.get_redirect_url() or reverse_lazy("dashboard")


def logout_view(request):
    """
    Logs out the user and redirects to the login page.
    """
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    #  Use namespaced URL to avoid NoReverseMatch
    return redirect(reverse_lazy("User_Login:login"))


def signup_view(request):
    """
    Handles user registration.
    On successful signup, redirects to the login page with a success message.
    """
    if request.method == "POST":
        form = SignupForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Account created successfully! You can now log in.")
            return redirect("User_Login:login")
    else:
        form = SignupForm()

    #  Template must exist: templates/User_Login/signup.html
    return render(request, "User_Login/signup.html", {"form": form})
