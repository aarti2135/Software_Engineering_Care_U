# healthdata/urls.py
from django.urls import path, include
from rest_framework.routers import SimpleRouter
from .views import (
    NutritionEntryViewSet,
    nutrition_dashboard,
    nutrition_edit,
    nutrition_delete,
)

router = SimpleRouter()
router.register('nutrition', NutritionEntryViewSet, basename='nutrition')

urlpatterns = [
    path('', include(router.urls)),
    path('dashboard/nutrition/', nutrition_dashboard, name='nutrition_dashboard'),
    path('dashboard/nutrition/<int:pk>/edit/', nutrition_edit, name='nutrition_edit'),
    path('dashboard/nutrition/<int:pk>/delete/', nutrition_delete, name='nutrition_delete'),
]
