# usermanagement/admin.py
from django.contrib import admin
from .models import Profile   # import from models.py (not a package)

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "age", "height_cm", "weight_kg", "sex")
    search_fields = ("user__username", "user__email")
    list_filter = ("sex",)
