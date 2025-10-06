from django.contrib import admin
from usermanagement.models.custom_user import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'data_sharing_consent')
    list_filter = ('data_sharing_consent',)
    search_fields = ('username',)
