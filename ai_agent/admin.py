from django.contrib import admin
from .models import ConversationHistory


@admin.register(ConversationHistory)
class ConversationHistoryAdmin(admin.ModelAdmin):
    """Admin interface for ConversationHistory model."""
    
    list_display = ['user', 'role', 'message_preview', 'session_id_short', 'created_at']
    list_filter = ['role', 'created_at', 'user']
    search_fields = ['message', 'user__username', 'user__email']
    readonly_fields = ['created_at', 'session_id']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Message Information', {
            'fields': ('user', 'session_id', 'role', 'message', 'created_at')
        }),
        ('Metadata', {
            'fields': ('metadata',),
            'classes': ('collapse',)
        }),
    )
    
    def message_preview(self, obj):
        """Show first 50 characters of message."""
        return obj.message[:50] + "..." if len(obj.message) > 50 else obj.message
    message_preview.short_description = 'Message Preview'
    
    def session_id_short(self, obj):
        """Show shortened session ID."""
        return str(obj.session_id)[:8] + "..."
    session_id_short.short_description = 'Session ID'
    
    def has_add_permission(self, request):
        """Disable manual creation - messages should only be created via API."""
        return False
    
    def has_change_permission(self, request, obj=None):
        """Make messages read-only - they're immutable conversation history."""
        return False
