from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Profile

class SignupForm(UserCreationForm):
    email = forms.EmailField(required=True, label="Email")
    age = forms.IntegerField(required=False, min_value=0, label="Age")
    height_cm = forms.IntegerField(required=False, min_value=0, label="Height (cm)")
    weight_kg = forms.DecimalField(required=False, min_value=0, max_digits=5, decimal_places=2, label="Weight (kg)")
    sex = forms.ChoiceField(required=False, choices=Profile.SEX_CHOICES, label="Sex")

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2", "age", "height_cm", "weight_kg", "sex")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        placeholders = {
            "username": "Choose a username",
            "email": "you@example.com",
            "password1": "Create password",
            "password2": "Confirm password",
            "age": "e.g. 23",
            "height_cm": "e.g. 175",
            "weight_kg": "e.g. 68.5",
        }
        for name, field in self.fields.items():
            field.widget.attrs.setdefault("class", "form-control")
            if name in placeholders:
                field.widget.attrs.setdefault("placeholder", placeholders[name])

    def save(self, commit=True):
        user = super().save(commit=commit)
        Profile.objects.update_or_create(
            user=user,
            defaults={
                "age": self.cleaned_data.get("age"),
                "height_cm": self.cleaned_data.get("height_cm"),
                "weight_kg": self.cleaned_data.get("weight_kg"),
                "sex": self.cleaned_data.get("sex"),
            },
        )
        return user
