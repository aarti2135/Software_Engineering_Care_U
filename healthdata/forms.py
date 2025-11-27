from django import forms
from .models import NutritionEntry, Goal


# ----------------------------------------------------------------------
# 🔹 Nutrition Entry Form
# ----------------------------------------------------------------------
class NutritionEntryForm(forms.ModelForm):
    """Form for adding or editing a nutrition entry."""
    class Meta:
        model = NutritionEntry
        exclude = ("user",)  # user is set in the view
        widgets = {
            "logged_at": forms.DateInput(attrs={
                "type": "date",
                "class": "form-control"
            }),
            "meal_type": forms.Select(attrs={"class": "form-select"}),
            "calories": forms.NumberInput(attrs={"min": 0, "class": "form-control"}),
            "protein_g": forms.NumberInput(attrs={"step": "0.01", "min": 0, "class": "form-control"}),
            "carbs_g": forms.NumberInput(attrs={"step": "0.01", "min": 0, "class": "form-control"}),
            "fat_g": forms.NumberInput(attrs={"step": "0.01", "min": 0, "class": "form-control"}),
            "notes": forms.Textarea(attrs={"rows": 2, "class": "form-control"}),
        }


# ----------------------------------------------------------------------
# 🔹 Goal Form
# ----------------------------------------------------------------------
class GoalForm(forms.ModelForm):
    """Form for creating or updating a health goal."""
    class Meta:
        model = Goal
        fields = [
            "title",
            "goal_type",
            "frequency",
            "target_value",
            "due_date",
            "notes",
        ]
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control", "placeholder": "e.g., Walk 10,000 steps daily"}),
            "goal_type": forms.Select(attrs={"class": "form-select"}),
            "frequency": forms.Select(attrs={"class": "form-select"}),
            "target_value": forms.NumberInput(attrs={"min": 0, "class": "form-control"}),
            "due_date": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "notes": forms.Textarea(attrs={"rows": 3, "class": "form-control", "placeholder": "Optional notes..."}),
        }
