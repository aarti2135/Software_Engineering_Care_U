from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse_lazy

class UserLoginView(LoginView):
    template_name = 'careu/login.html'
    redirect_authenticated_user = True

class UserLogoutView(LogoutView):
    next_page = reverse_lazy('login')
