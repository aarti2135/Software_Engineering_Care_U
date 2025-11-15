"""
API Views for AI Agent
"""

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.permissions import IsAuthenticated
import logging

from ai_agent.services import AIAgentService
from ai_agent.serializers import (
    ChatRequestSerializer,
    ChatResponseSerializer,
    ErrorResponseSerializer
)

logger = logging.getLogger(__name__)


class ChatAPIView(APIView):
    """
    API endpoint for AI agent chat.
    
    POST /api/agent/chat/
    
    Request Body:
    {
        "message": "What's my recommended protein intake?",
        "session_id": "optional-uuid-or-null",
        "days_to_analyze": 7  // optional, 7-30
    }
    
    Response:
    {
        "response": "Based on your 70kg weight...",
        "session_id": "uuid",
        "metadata": {
            "data_sources_used": ["nutrition_last_7_days", "profile"],
            "calculations": {"bmr": 1650, "tdee": 2558, "protein_target": 84}
        }
    }
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """
        Process a user message and return AI response.
        """
        # Validate request data
        serializer = ChatRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {
                    "error": "Invalid request data",
                    "details": serializer.errors
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        message = serializer.validated_data['message']
        session_id = serializer.validated_data.get('session_id')
        days_to_analyze = serializer.validated_data.get('days_to_analyze', 7)

        # Validate message is not empty
        if not message or not message.strip():
            return Response(
                {
                    "error": "Message cannot be empty"
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # Initialize AI agent service
            agent_service = AIAgentService(request.user)

            # Process message
            result = agent_service.process_message(
                message=message.strip(),
                session_id=session_id,
                days_to_analyze=days_to_analyze
            )

            # Check for errors
            if result.get('error'):
                logger.error(f"AI agent error for user {request.user.id}: {result['error']}")
                return Response(
                    {
                        "error": "Unable to process request. Please try again later.",
                        "details": result['error']
                    },
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

            # Return successful response
            response_serializer = ChatResponseSerializer({
                "response": result['response'],
                "session_id": result['session_id'],
                "metadata": result['metadata']
            })

            return Response(response_serializer.data, status=status.HTTP_200_OK)

        except ValueError as e:
            # Missing API key or configuration error
            logger.error(f"Configuration error for user {request.user.id}: {str(e)}")
            return Response(
                {
                    "error": "AI service is not properly configured. Please contact support.",
                    "details": str(e)
                },
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )

        except Exception as e:
            # Unexpected error
            logger.error(f"Unexpected error processing message for user {request.user.id}: {str(e)}", exc_info=True)
            return Response(
                {
                    "error": "An unexpected error occurred. Please try again later.",
                    "details": str(e) if request.user.is_staff else None  # Only show details to staff
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
