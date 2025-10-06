from django.conf import settings
from django.db import models
from django.utils import timezone

class NutritionEntry(models.Model):
    MEAL_CHOICES = [
        ("breakfast", "Breakfast"),
        ("lunch", "Lunch"),
        ("dinner", "Dinner"),
        ("snack", "Snack"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="nutrition_entries",
    )
    logged_at = models.DateField(default=timezone.now)
    meal_type = models.CharField(max_length=16, choices=MEAL_CHOICES)
    calories = models.PositiveIntegerField()
    protein_g = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    carbs_g = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    fat_g = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-logged_at", "-created_at"]

    def __str__(self):
        return f"{self.user} {self.meal_type} on {self.logged_at} ({self.calories} kcal)"
