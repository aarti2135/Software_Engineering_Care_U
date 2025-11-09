# healthdata/urls.py
from django.urls import path, include
from rest_framework.routers import SimpleRouter
from . import views

router = SimpleRouter()
router.register('nutrition', views.NutritionEntryViewSet, basename='nutrition')
router.register('reminders', views.HealthReminderViewSet, basename='reminders')
router.register('glucose', views.GlucoseEntryViewSet, basename='glucose')
router.register('medication', views.MedicationEntryViewSet, basename='medication')
router.register('doctornotes', views.DoctorNoteViewSet, basename='doctornotes')
router.register('vitals', views.VitalLogViewSet, basename='vitals')
router.register('mood', views.MoodLogViewSet, basename='mood')
router.register('symptoms', views.SymptomLogViewSet, basename='symptoms')
router.register('habits', views.HabitLogViewSet, basename='habits')
router.register('wellbeing', views.WellbeingLogViewSet, basename='wellbeing')

urlpatterns = [
    # Dashboard home
    path('', views.home_dashboard, name='dashboard'),

    # Nutrition
    path('nutrition/', views.nutrition_dashboard, name='nutrition_dashboard'),
    path('nutrition/import/', views.nutrition_import, name='nutrition_import'),
    path('nutrition/<int:pk>/edit/', views.nutrition_edit, name='nutrition_edit'),
    path('nutrition/<int:pk>/delete/', views.nutrition_delete, name='nutrition_delete'),

    # Reminders
    path('reminders/', views.reminders_dashboard, name='reminders_dashboard'),
    path('reminders/<int:pk>/dismiss/', views.dismiss_reminder, name='dismiss_reminder'),
    path('reminders/<int:pk>/act/', views.act_on_reminder, name='act_on_reminder'),

    # Goals
    path('goals/', views.goal_dashboard, name='goal_dashboard'),
    path('goals/create/', views.goal_create, name='goal_create'),
    path('goals/<int:pk>/edit/', views.goal_edit, name='goal_edit'),
    path('goals/<int:pk>/delete/', views.goal_delete, name='goal_delete'),

    # API
    path('', include(router.urls)),
]
