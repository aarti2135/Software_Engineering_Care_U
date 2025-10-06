from django import forms
from .models import NutritionEntry

class NutritionEntryForm(forms.ModelForm):
    class Meta:
        model = NutritionEntry
        exclude = ("user",)  # user is set in the view
        widgets = {
            "logged_at": forms.DateInput(attrs={"type": "date"}),
            "meal_type": forms.Select(),
            "calories": forms.NumberInput(attrs={"min": 0}),
            "protein_g": forms.NumberInput(attrs={"step": "0.01", "min": 0}),
            "carbs_g": forms.NumberInput(attrs={"step": "0.01", "min": 0}),
            "fat_g": forms.NumberInput(attrs={"step": "0.01", "min": 0}),
            "notes": forms.Textarea(attrs={"rows": 2}),
        }
