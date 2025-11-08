# User_Login/urls.py
from django.urls import path
from .views import UserLoginView, logout_view, signup_view

# Define the app namespace so you can reference these URLs safely from templates
app_name = "User_Login"

urlpatterns = [
    # Login page (blue theme)
    path("login/", UserLoginView.as_view(), name="login"),

    # Logout view (GET-safe, redirects to login page)
    path("logout/", logout_view, name="logout"),

    # Signup page (new user registration)
    path("signup/", signup_view, name="signup"),
]
