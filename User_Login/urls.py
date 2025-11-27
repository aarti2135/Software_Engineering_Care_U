# User_Login/urls.py
from django.urls import path
from .views import UserLoginView, logout_view, signup_view

#  Namespace allows safe reverse lookups:  {% url 'User_Login:login' %}
app_name = "User_Login"

urlpatterns = [
    #  Login page (renders the blue-gradient login form)
    path("login/", UserLoginView.as_view(), name="login"),

    #  Logout view (handles GET or POST, redirects to login page)
    path("logout/", logout_view, name="logout"),

    #  Signup page (new user registration form)
    path("signup/", signup_view, name="signup"),
]
