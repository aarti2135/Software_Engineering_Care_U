"""
AI Agent Services

Core service classes for processing user health data and generating
personalized AI responses using Gemini API.
"""

import uuid
from datetime import timedelta
from typing import Optional, Dict, List, Any
from django.utils import timezone
from django.db.models import Avg, Sum, Count
from django.conf import settings

from healthdata.models import NutritionEntry, HealthReminder
from healthdata.reminders_engine import HealthCalculator
from ai_agent.models import ConversationHistory
from ai_agent.gemini_client import GeminiClient
import logging

logger = logging.getLogger(__name__)

# Safety disclaimer that must be included in all responses
SAFETY_DISCLAIMER = (
    "\n\n⚠️ **Disclaimer**: This information is for educational purposes only. "
    "Consider discussing this with your doctor before making significant health changes."
)


class HealthDataAggregator:
    """
    Aggregates and processes user health data (nutrition, sleep, activity).
    """

    @staticmethod
    def get_nutrition_data(user, days=7):
        """
        Get aggregated nutrition data for the last N days.
        
        Args:
            user: User instance
            days: Number of days to look back (default 7, max 30)
        
        Returns:
            dict: Aggregated nutrition data with averages and totals
        """
        days = min(days, 30)  # Cap at 30 days
        start_date = timezone.localdate() - timedelta(days=days)
        
        entries = NutritionEntry.objects.filter(
            user=user,
            logged_at__gte=start_date
        )
        
        if not entries.exists():
            return {
                "has_data": False,
                "days_analyzed": 0,
                "average_calories": None,
                "average_protein": None,
                "average_carbs": None,
                "average_fat": None,
                "total_entries": 0,
                "days_with_entries": 0,
            }
        
        # Calculate averages
        agg = entries.aggregate(
            avg_calories=Avg('calories'),
            avg_protein=Avg('protein_g'),
            avg_carbs=Avg('carbs_g'),
            avg_fat=Avg('fat_g'),
            total_entries=Count('id'),
        )
        
        # Count distinct days with entries
        days_with_entries = entries.values('logged_at').distinct().count()
        
        return {
            "has_data": True,
            "days_analyzed": days,
            "average_calories": round(agg['avg_calories'] or 0, 1),
            "average_protein": round(float(agg['avg_protein'] or 0), 1),
            "average_carbs": round(float(agg['avg_carbs'] or 0), 1),
            "average_fat": round(float(agg['avg_fat'] or 0), 1),
            "total_entries": agg['total_entries'],
            "days_with_entries": days_with_entries,
            "logging_consistency": round((days_with_entries / days) * 100, 1),
        }


class ContextBuilder:
    """
    Builds comprehensive user context for AI prompts.
    Includes profile data, health metrics, and active reminders.
    """

    def __init__(self, user):
        self.user = user
        self.profile = user.profile
        self.calculator = HealthCalculator()

    def build_user_context(self, nutrition_data=None, include_reminders=True):
        """
        Build comprehensive user context string for AI prompts.
        
        Args:
            nutrition_data: Optional nutrition data dict from HealthDataAggregator
            include_reminders: Whether to include active health reminders
        
        Returns:
            dict: {
                "context": str,  # Formatted context string
                "calculations": dict,  # BMR, TDEE, protein targets
                "has_complete_profile": bool,
                "active_reminders": list  # List of active reminders
            }
        """
        context_parts = []
        calculations = {}
        has_complete_profile = False

        # ----------------------------
        # Profile information
        # ----------------------------
        profile_info = []
        if self.profile:
            if self.profile.age:
                profile_info.append(f"Age: {self.profile.age} years")
            if self.profile.weight_kg:
                profile_info.append(f"Weight: {self.profile.weight_kg} kg")
            if self.profile.height_cm:
                profile_info.append(f"Height: {self.profile.height_cm} cm")
            if self.profile.sex:
                profile_info.append(f"Sex: {self.profile.get_sex_display()}")
            if self.profile.activity_level:
                profile_info.append(f"Activity Level: {self.profile.get_activity_level_display()}")

            if profile_info:
                context_parts.append("**User Profile:**")
                context_parts.append("\n".join(profile_info))
                has_complete_profile = True
            else:
                context_parts.append("**User Profile:** Incomplete profile data available.")
        profile_summary = "\n".join(profile_info) if profile_info else "Profile information is incomplete."
        
        # Health metrics calculations
        if has_complete_profile:
            bmr = self.calculator.calculate_bmr(self.profile)
            tdee = self.calculator.calculate_tdee(self.profile)
            protein_target = self.calculator.calculate_protein_target(self.profile)
            activity_level = self.calculator.get_activity_level(self.profile)
            
            if bmr:
                calculations['bmr'] = round(bmr, 1)
                context_parts.append(f"\n**Calculated Health Metrics:**")
                context_parts.append(f"- Basal Metabolic Rate (BMR): {bmr:.1f} calories/day")
            
            if tdee:
                calculations['tdee'] = round(tdee, 1)
                context_parts.append(f"- Total Daily Energy Expenditure (TDEE): {tdee:.1f} calories/day")
            
            if protein_target:
                calculations['protein_target'] = round(protein_target, 1)
                context_parts.append(f"- Recommended Daily Protein Target: {protein_target:.1f} grams/day")
                context_parts.append(f"- Activity Level: {activity_level}")
        
        # ----------------------------
        # Nutrition data summary
        # ----------------------------
        health_lines = []
        if nutrition_data and nutrition_data.get('has_data'):
            context_parts.append(f"\n**Recent Nutrition Data (Last {nutrition_data['days_analyzed']} days):**")
            context_parts.append(f"- Average Daily Calories: {nutrition_data['average_calories']:.1f} kcal")

            if nutrition_data.get('average_protein') is not None:
                context_parts.append(f"- Average Daily Protein: {nutrition_data['average_protein']:.1f} g")
            if nutrition_data.get('average_carbs') is not None:
                context_parts.append(f"- Average Daily Carbs: {nutrition_data['average_carbs']:.1f} g")
            if nutrition_data.get('average_fat') is not None:
                context_parts.append(f"- Average Daily Fat: {nutrition_data['average_fat']:.1f} g")

            context_parts.append(
                f"- Logging Consistency: {nutrition_data['logging_consistency']:.1f}% "
                f"({nutrition_data['days_with_entries']} out of {nutrition_data['days_analyzed']} days)"
            )

            health_lines.append(
                f"Average daily calories over the last {nutrition_data['days_analyzed']} days: "
                f"{nutrition_data['average_calories']:.1f} kcal."
            )
            if nutrition_data.get('average_protein') is not None:
                health_lines.append(f"Average daily protein: {nutrition_data['average_protein']:.1f} g.")
            if nutrition_data.get('average_carbs') is not None:
                health_lines.append(f"Average daily carbs: {nutrition_data['average_carbs']:.1f} g.")
            if nutrition_data.get('average_fat') is not None:
                health_lines.append(f"Average daily fat: {nutrition_data['average_fat']:.1f} g.")
            health_lines.append(
                f"Logging consistency: {nutrition_data['logging_consistency']:.1f}% "
                f"({nutrition_data['days_with_entries']} of {nutrition_data['days_analyzed']} days)."
            )
        elif nutrition_data:
            context_parts.append("\n**Nutrition Data:** No nutrition data available for analysis.")
            health_lines.append("No recent nutrition data is available.")
        else:
            health_lines.append("No recent nutrition data is available.")

        health_summary = "\n".join(health_lines)

        # ----------------------------
        # Active reminders (summary + detailed list)
        # ----------------------------
        active_reminders = []
        reminders_summary_lines = []
        if include_reminders:
            reminders = HealthReminder.objects.filter(
                user=self.user,
                dismissed_at__isnull=True
            ).order_by('-priority', '-created_at')[:5]  # Limit to 5 most recent

            if reminders.exists():
                context_parts.append("\n**Active Health Reminders:**")
                for reminder in reminders:
                    reminder_info = f"- {reminder.title} ({reminder.get_priority_display()} priority)"
                    reminder_info += f"\n  Message: {reminder.message}"
                    reminder_info += f"\n  Explanation: {reminder.explanation}"
                    if reminder.actionable_steps:
                        reminder_info += f"\n  Actionable Steps: {', '.join(reminder.actionable_steps[:3])}"
                    context_parts.append(reminder_info)

                    reminders_summary_lines.append(
                        f"- {reminder.title} ({reminder.get_priority_display()} priority): {reminder.message}"
                    )

                    active_reminders.append({
                        'title': reminder.title,
                        'message': reminder.message,
                        'explanation': reminder.explanation,
                        'priority': reminder.priority,
                        'type': reminder.reminder_type,
                        'actionable_steps': reminder.actionable_steps,
                    })
            else:
                reminders_summary_lines.append("No active reminders.")
        else:
            reminders_summary_lines.append("No active reminders.")

        reminders_summary = "\n".join(reminders_summary_lines)
        
        context_string = "\n".join(context_parts)

        return {
            "context": context_string,
            "calculations": calculations,
            "has_complete_profile": has_complete_profile,
            "active_reminders": active_reminders,
            "profile_summary": profile_summary,
            "health_summary": health_summary,
            "reminders_summary": reminders_summary,
        }


class ConversationManager:
    """
    Manages conversation history for maintaining context across messages.
    """

    @staticmethod
    def get_or_create_session(user, session_id=None):
        """
        Get or create a session ID for the user.
        If no session_id provided, gets the most recent active session or creates new one.
        
        Args:
            user: User instance
            session_id: Optional UUID for session
        
        Returns:
            UUID: Session ID
        """
        if session_id:
            try:
                # Validate that this session belongs to the user
                session_uuid = uuid.UUID(str(session_id))
                if ConversationHistory.objects.filter(
                    user=user,
                    session_id=session_uuid
                ).exists():
                    return session_uuid
                # Session doesn't belong to user or doesn't exist, create new one
            except ValueError:
                # Invalid UUID format, create new one
                pass
        
        # Get most recent session for user (within last 24 hours)
        day_ago = timezone.now() - timedelta(hours=24)
        recent_session = ConversationHistory.objects.filter(
            user=user,
            created_at__gte=day_ago
        ).values('session_id').distinct().order_by('-created_at').first()
        
        if recent_session:
            return recent_session['session_id']
        
        # Create new session
        return uuid.uuid4()

    @staticmethod
    def get_conversation_history(user, session_id, limit=20):
        """
        Get conversation history for a session.
        
        Args:
            user: User instance
            session_id: UUID of the session
            limit: Maximum number of messages to retrieve
        
        Returns:
            QuerySet: ConversationHistory objects ordered by created_at
        """
        return ConversationHistory.objects.filter(
            user=user,
            session_id=session_id
        ).order_by('-created_at')[:limit]

    @staticmethod
    def save_message(user, session_id, role, message, metadata=None):
        """
        Save a message to conversation history.
        
        Args:
            user: User instance
            session_id: UUID of the session
            role: 'user' or 'assistant'
            message: Message content
            metadata: Optional metadata dict to store
        
        Returns:
            ConversationHistory: Created message object
        """
        return ConversationHistory.objects.create(
            user=user,
            session_id=session_id,
            role=role,
            message=message,
            metadata=metadata or {}
        )


class AIAgentService:
    """
    Main orchestrator service for AI agent interactions.
    Processes user messages, builds context, and generates personalized responses.
    """

    def __init__(self, user):
        self.user = user
        self.gemini_client = None
        self.data_aggregator = HealthDataAggregator()
        self.context_builder = ContextBuilder(user)
        self.conversation_manager = ConversationManager()
        
        # Initialize Gemini client
        try:
            self.gemini_client = GeminiClient()
        except Exception as e:
            logger.error(f"Failed to initialize Gemini client: {str(e)}")
            raise

    def _detect_reminder_query(self, message):
        """
        Detect if user is asking about health reminders.
        
        Args:
            message: User's message
        
        Returns:
            bool: True if message seems to be about reminders
        """
        message_lower = message.lower()
        reminder_keywords = [
            'reminder', 'reminders', 'why', 'explain', 'reason',
            'getting this', 'what is this', 'tell me about'
        ]
        
        return any(keyword in message_lower for keyword in reminder_keywords)

    def _is_casual_message(self, message: str) -> bool:
        """
        Very simple heuristic to detect greetings / small talk.
        """
        if not message:
            return False
        text = message.strip().lower()
        short = len(text) <= 25

        casual_phrases = [
            "hi", "hey", "hello", "yo", "good morning", "good evening",
            "what's up", "whats up", "how are you", "how's it going",
            "how are you doing"
        ]

        return short and any(text == p or text.startswith(p) for p in casual_phrases)

    def _build_system_prompt(self, user_context, is_reminder_query=False, is_casual=False):
        """
        Build the system prompt for Gemini API.

        Args:
            user_context: Context dict from ContextBuilder
            is_reminder_query: Whether user is asking about reminders
            is_casual: Whether the message looks like casual small talk / greeting

        Returns:
            str: System prompt
        """
        profile_summary = user_context.get("profile_summary", "Profile information is incomplete.")
        health_summary = user_context.get("health_summary", "")
        reminders_summary = user_context.get("reminders_summary", "No active reminders.")

        prompt_parts = [
            "You are a friendly AI health assistant for CareU, a personalized health tracking app.",
            "",
            "**CONVERSATION STYLE:**",
            "- Respond naturally to greetings and small talk WITHOUT forcing health data.",
            "- Only dive into health metrics when the user asks specific questions.",
            "- Be warm, encouraging, and human-like.",
            "- Ask clarifying questions when needed.",
            "",
            "**WHEN TO REFERENCE USER DATA:**",
            "✅ User asks 'why this reminder?' → Explain that reminder using their data.",
            "✅ User asks about nutrition/activity/sleep → Show relevant numbers from their data.",
            "✅ User asks for advice → Base it on their profile (age, weight, activity level).",
            "❌ User just says 'hi', 'hey', etc. → Greet them and ask how you can help, do NOT dump data.",
            "",
            "**SAFETY RULES:**",
            "- Never diagnose medical conditions or prescribe treatments.",
            "- Suggest consulting healthcare providers for medical concerns.",
            "- DO NOT include any disclaimer text; the system will add it automatically.",
            "",
            "**USER PROFILE:**",
            profile_summary,
        ]

        # Only include more detailed data when it's actually useful
        if not is_casual:
            prompt_parts.extend([
                "",
                "**RECENT HEALTH DATA (only reference if relevant to the question):**",
                health_summary,
                "",
                "**ACTIVE REMINDERS (only explain if the user asks about them):**",
                reminders_summary,
            ])

        # Extra guidance for explicit reminder questions
        if is_reminder_query:
            prompt_parts.extend([
                "",
                "The user is asking about their reminders. Focus on explaining WHY they are seeing specific reminders,",
                "and how they connect to the data described above. Do not invent sources that weren't provided.",
            ])

        prompt_parts.extend([
            "",
            "**RESPONSE STYLE:**",
            "- Keep responses clear and concise.",
            "- Avoid markdown headings; simple paragraphs and short lists are fine.",
            "- Speak directly to the user ('you') and keep a conversational tone.",
        ])

        return "\n".join(prompt_parts)

    def process_message(self, message, session_id=None, days_to_analyze=7):
        """
        Process a user message and generate AI response.
        
        Args:
            message: User's message
            session_id: Optional session ID (creates new if not provided)
            days_to_analyze: Number of days of nutrition data to analyze (7-30)
        
        Returns:
            dict: {
                "response": str,  # AI response
                "session_id": UUID,  # Session ID
                "metadata": dict,  # Metadata about data sources and calculations
                "error": str or None  # Error message if failed
            }
        """
        try:
            # Get or create session
            session_id = self.conversation_manager.get_or_create_session(
                self.user, session_id
            )
            
            # Get nutrition data
            nutrition_data = self.data_aggregator.get_nutrition_data(
                self.user, days=min(days_to_analyze, 30)
            )
            
            # Build user context
            is_reminder_query = self._detect_reminder_query(message)
            is_casual = self._is_casual_message(message)

            # Always include reminders in context so the model can use them when needed,
            # but the prompt will control when they are referenced.
            user_context = self.context_builder.build_user_context(
                nutrition_data=nutrition_data,
                include_reminders=True
            )

            # Build system prompt (different behavior for casual chat vs data questions)
            system_prompt = self._build_system_prompt(
                user_context,
                is_reminder_query=is_reminder_query,
                is_casual=is_casual,
            )
            
            # Get conversation history
            history_messages = self.conversation_manager.get_conversation_history(
                self.user, session_id, limit=20
            )
            
            # Format history for Gemini API (reverse order - oldest first)
            formatted_history = []
            if history_messages.exists():
                # Reverse to get chronological order
                messages_list = list(reversed(history_messages))
                formatted_history = self.gemini_client.format_conversation_history(
                    messages_list
                )
            
            # For Gemini API, include system prompt in the user message if no history exists
            # Otherwise, send system prompt + user message as the current message
            if formatted_history:
                # Has history: send system context + user message
                full_prompt = f"{system_prompt}\n\n**User Question:** {message}"
                result = self.gemini_client.generate_response(
                    prompt=full_prompt,
                    context_history=formatted_history,
                    temperature=0.7
                )
            else:
                # First message: include system prompt in the initial message
                full_prompt = f"{system_prompt}\n\n**User Question:** {message}"
                result = self.gemini_client.generate_response(
                    prompt=full_prompt,
                    context_history=None,
                    temperature=0.7
                )
            
            if result.get('error'):
                return {
                    "response": None,
                    "session_id": session_id,
                    "metadata": {},
                    "error": result['error']
                }
            
            # Add safety disclaimer to response.
            # First strip any disclaimer text the model may have added itself,
            # then append a single standardized disclaimer.
            raw_text = result['response'] or ""
            cleaned_text = raw_text.replace(SAFETY_DISCLAIMER, "").strip()
            response_text = cleaned_text + SAFETY_DISCLAIMER
            
            # Save user message
            self.conversation_manager.save_message(
                self.user, session_id, 'user', message,
                metadata={'days_analyzed': days_to_analyze}
            )
            
            # Save assistant response
            metadata = {
                'data_sources_used': [],
                'calculations': user_context['calculations'],
            }
            
            if nutrition_data.get('has_data'):
                metadata['data_sources_used'].append(f'nutrition_last_{days_to_analyze}_days')
            if user_context['has_complete_profile']:
                metadata['data_sources_used'].append('profile')
            if user_context.get('active_reminders'):
                metadata['data_sources_used'].append('active_reminders')
                metadata['reminder_count'] = len(user_context['active_reminders'])
            
            self.conversation_manager.save_message(
                self.user, session_id, 'assistant', response_text,
                metadata=metadata
            )
            
            return {
                "response": response_text,
                "session_id": str(session_id),
                "metadata": metadata,
                "error": None
            }
            
        except Exception as e:
            error_msg = f"Failed to process message: {str(e)}"
            logger.error(error_msg, exc_info=True)
            
            return {
                "response": None,
                "session_id": str(session_id) if session_id else None,
                "metadata": {},
                "error": error_msg
            }

