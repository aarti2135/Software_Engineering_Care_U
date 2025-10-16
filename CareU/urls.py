# CareU/urls.py
from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect
from usermanagement.views import consent_urls


def home_redirect(request):
    """
    Redirect the root URL depending on authentication:
      - If logged in  → go to the nutrition dashboard
      - If anonymous  → go to login page
    """
    if request.user.is_authenticated:
        return redirect('nutrition_dashboard')  # Must exist in healthdata.urls
    else:
        return redirect('User_Login:login')  # Namespaced login route


urlpatterns = [
    # Root redirect (home)
    path('', home_redirect, name='home'),

    # Admin panel
    path('admin/', admin.site.urls),
    path('', include(consent_urls)),

    # Health / API routes (nutrition dashboard, etc.)
    path('api/', include('healthdata.urls')),

    # Django REST Framework browsable API auth
    path('api-auth/', include('rest_framework.urls')),

    # User login / logout / signup (with namespace)
    path(
        'accounts/',
        include(('User_Login.urls', 'User_Login'), namespace='User_Login')
    ),
]
