# CareU/urls.py
from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect


def home_redirect(request):
    """
    Root redirect:
    - Authenticated users → dashboard
    - Anonymous users → login
    """
    if request.user.is_authenticated:
        return redirect('dashboard')
    else:
        return redirect('User_Login:login')


urlpatterns = [
    # Root redirect
    path('', home_redirect, name='home'),

    # Admin site
    path('admin/', admin.site.urls),

    # ✅ Healthdata (nutrition, goals, reminders, etc.)
    path('dashboard/', include('healthdata.urls')),  # ✅ add "dashboard/" prefix here

    # ✅ Proactive / AI features
    path('proactive/', include('proactive_feat.urls')),

    # ✅ User management (consent, provider alerts)
    path('user/', include('usermanagement.urls')),

    # ✅ Authentication (login, logout, signup)
    path(
        'accounts/',
        include(('User_Login.urls', 'User_Login'), namespace='User_Login'),
    ),

    # ✅ Django REST Framework browsable API auth
    path('api-auth/', include('rest_framework.urls')),
]
