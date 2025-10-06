# usermanagement/admin.py
from django.contrib import admin
from .models import Profile

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "age", "height_cm", "weight_kg", "sex", "bmi")
    search_fields = ("user__username", "user__email")
    list_filter = ("sex",)
