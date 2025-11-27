# CareU/urls.py
from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views


def home_redirect(request):
    """
    Root redirect:
    - Authenticated users → main dashboard
    - Anonymous users → login
    """
    if request.user.is_authenticated:
        return redirect('dashboard')  # Main home dashboard (healthdata)
    else:
        return redirect('User_Login:login')  # Namespaced login route


urlpatterns = [
    # ------------------------------------------------------------------
    # Root redirect & admin
    # ------------------------------------------------------------------
    path('', home_redirect, name='home'),
    path('admin/', admin.site.urls),

    # ------------------------------------------------------------------
    # Healthdata module (nutrition, goals, reminders)
    # ------------------------------------------------------------------
    path('dashboard/', include('healthdata.urls')),  # ✅ consistent path prefix

    # ------------------------------------------------------------------
    # Proactive / AI module
    # ------------------------------------------------------------------
    path(
        'proactive/',
        include(('proactive_feat.urls', 'proactive_feat'), namespace='proactive_feat'),
    ),

    # ------------------------------------------------------------------
    # User management (consent, provider alerts)
    # ------------------------------------------------------------------
    path('user/', include('usermanagement.urls')),

    # ------------------------------------------------------------------
    # Analytics & Insights (✅ from analytics branch)
    # ------------------------------------------------------------------
    path('analytics/', include('analytics.urls')),

    # ------------------------------------------------------------------
    # Motivation / Avatar module
    # ------------------------------------------------------------------
    path('motivation/', include('motivation.urls')),


    path('gamification/', include('gamification.urls')),
    path('logout/', auth_views.LogoutView.as_view(next_page='User_Login:login'), name='logout'),  # Add this line

    # ------------------------------------------------------------------
    # Authentication (login, logout, signup)
    # ------------------------------------------------------------------
    path('accounts/', include(('User_Login.urls', 'User_Login'), namespace='User_Login'),),

    # ------------------------------------------------------------------
    # Django REST Framework browsable API
    # ------------------------------------------------------------------
    path('api-auth/', include('rest_framework.urls')),

    # ------------------------------------------------------------------
    # AI Agent API
    # ------------------------------------------------------------------
    path('api/agent/', include('ai_agent.urls')),

]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)