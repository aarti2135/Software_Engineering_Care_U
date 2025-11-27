from django.db.models.signals import post_save
from django.dispatch import receiver
from healthdata.models import NutritionEntry
from .services import GamificationService


@receiver(post_save, sender=NutritionEntry)
def update_gamification_on_nutrition_entry(sender, instance, created, **kwargs):
    """Auto-update gamification when nutrition entry is created"""
    if created:
        service = GamificationService(instance.user)
        service.record_activity()