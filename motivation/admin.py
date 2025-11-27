from django.contrib import admin
from .models import Avatar, UserProfile

@admin.register(Avatar)
class AvatarAdmin(admin.ModelAdmin):
    list_display = ("name",)

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "avatar")
