# User_Login/views.py
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import logout
from usermanagement.forms import SignupForm


class UserLoginView(LoginView):
    """
    Login page using the blue gradient template located at templates/careu/login.html.
    Redirects authenticated users straight to the dashboard.
    """
    template_name = "careu/login.html"
    redirect_authenticated_user = True

    def get_success_url(self):
        """
        After successful login, redirect the user to the nutrition dashboard.
        """
        return reverse_lazy("nutrition_dashboard")


def logout_view(request):
    """
    Logs out the user safely using GET or POST and redirects to the login page.
    Also displays a confirmation message.
    """
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    # ✅ Use namespaced URL to avoid NoReverseMatch
    return redirect(reverse_lazy("User_Login:login"))


def signup_view(request):
    """
    Handles user registration.
    On successful signup, redirects to the login page with a success message.
    """
    if request.method == "POST":
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()  # Creates the user instance (profile via signals if any)
            messages.success(request, "Account created successfully! You can now log in.")
            # ✅ Use namespaced URL here too
            return redirect("User_Login:login")
    else:
        form = SignupForm()

    # ✅ Make sure this template exists: templates/User_Login/signup.html
    return render(request, "User_Login/signup.html", {"form": form})
