# ai_agent/models.py
import uuid
from django.db import models
from django.conf import settings
from django.utils import timezone


class ConversationHistory(models.Model):
    """
    Stores individual messages in a conversation between user and AI agent.
    Each row represents ONE message (either from user or assistant).
    Messages with the same session_id belong to the same conversation.
    """

    ROLE_CHOICES = [
        ('user', 'User'),
        ('assistant', 'Assistant'),
    ]

    # Link to the user who owns this conversation
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='ai_conversations'
    )

    # Groups messages into a single conversation session
    session_id = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        db_index=True  # Index for fast lookups by session
    )

    # Who sent this message: 'user' or 'assistant'
    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES
    )

    # The actual message content
    message = models.TextField()

    # When this message was sent
    created_at = models.DateTimeField(
        default=timezone.now,
        db_index=True
    )

    # Optional: Store metadata (e.g., data sources used, calculations)
    metadata = models.JSONField(
        null=True,
        blank=True,
        help_text="Additional context like data sources, calculations, etc."
    )

    class Meta:
        ordering = ['created_at']  # Oldest first (for conversation flow)
        verbose_name_plural = 'Conversation Histories'
        indexes = [
            # Composite index for efficient queries: "get all messages for user X in session Y"
            models.Index(fields=['user', 'session_id', 'created_at']),
        ]

    def __str__(self):
        preview = self.message[:50] + "..." if len(self.message) > 50 else self.message
        return f"{self.role.title()}: {preview} ({self.session_id.hex[:8]})"