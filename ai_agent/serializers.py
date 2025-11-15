"""
Serializers for AI Agent API
"""

from rest_framework import serializers


class ChatRequestSerializer(serializers.Serializer):
    """Serializer for chat API request."""
    message = serializers.CharField(
        required=True,
        help_text="User's message to the AI agent"
    )
    session_id = serializers.UUIDField(
        required=False,
        allow_null=True,
        help_text="Optional session ID for conversation continuity"
    )
    days_to_analyze = serializers.IntegerField(
        required=False,
        default=7,
        min_value=7,
        max_value=30,
        help_text="Number of days of nutrition data to analyze (7-30)"
    )


class ChatResponseSerializer(serializers.Serializer):
    """Serializer for chat API response."""
    response = serializers.CharField(
        help_text="AI agent's response"
    )
    session_id = serializers.UUIDField(
        help_text="Session ID for this conversation"
    )
    metadata = serializers.DictField(
        help_text="Metadata about data sources and calculations used"
    )


class ErrorResponseSerializer(serializers.Serializer):
    """Serializer for error responses."""
    error = serializers.CharField(
        help_text="Error message"
    )
    details = serializers.CharField(
        required=False,
        allow_null=True,
        help_text="Additional error details"
    )

