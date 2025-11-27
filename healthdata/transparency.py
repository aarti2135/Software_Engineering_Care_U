# healthdata/transparency.py
"""
Transparency tracking for health reminders.
Shows users how recommendations are generated.
"""

from datetime import timedelta
from django.utils import timezone


class TransparencyLabel:
    """
    Generates transparency labels for reminders.
    Shows users the data sources behind recommendations.
    """

    SOURCE_TYPES = {
        'personal_data': '📊 Based on your personal data',
        'guidelines': '📖 Based on health guidelines',
        'ai_insight': '🤖 AI-generated insight',
        'combined': '🔍 Based on your data + guidelines'
    }

    @staticmethod
    def get_label_for_reminder(reminder):
        """
        Generate transparency label for a reminder.

        Args:
            reminder: HealthReminder instance

        Returns:
            dict: {
                'source_type': str,
                'label': str,
                'short_label': str,
                'explanation': str,
                'data_points': list
            }
        """
        # Start from whatever metadata we have (or empty dict)
        metadata = getattr(reminder, "metadata", None) or {}
        rtype = getattr(reminder, "reminder_type", None)
        data_sources = metadata.get('data_sources_used', [])

        # ---------- NUTRITION-BASED REMINDERS ----------
        if rtype == 'nutrition' or 'nutrition' in data_sources:
            # default days window
            days = metadata.get('days_analyzed', 7)

            # Try to read from metadata first
            avg_calories = metadata.get('avg_calories')
            avg_protein = metadata.get('avg_protein')
            total_entries = metadata.get('total_entries')
            days_with_entries = metadata.get('days_with_entries')

            # If any of these is missing, FALL BACK to live DB query
            if (
                avg_calories is None or
                avg_protein is None or
                total_entries is None or
                days_with_entries is None
            ):
                from healthdata.models import NutritionEntry
                from django.db.models import Avg, Count

                end_date = timezone.localdate()
                start_date = end_date - timedelta(days=days)

                entries = NutritionEntry.objects.filter(
                    user=reminder.user,
                    logged_at__gte=start_date,
                    logged_at__lte=end_date
                )

                if entries.exists():
                    agg = entries.aggregate(
                        avg_calories=Avg('calories'),
                        avg_protein=Avg('protein_g'),
                        total_entries=Count('id'),
                    )

                    avg_calories = round(agg['avg_calories'] or 0, 1)
                    avg_protein = round(float(agg['avg_protein'] or 0), 1)
                    total_entries = agg['total_entries']
                    days_with_entries = entries.values('logged_at').distinct().count()
                else:
                    # No data at all in window
                    avg_calories = None
                    avg_protein = None
                    total_entries = 0
                    days_with_entries = 0

                # Optionally persist back into metadata (if model has this field)
                if hasattr(reminder, "metadata"):
                    metadata.update({
                        'data_sources_used': metadata.get('data_sources_used', ['nutrition']),
                        'days_analyzed': days,
                        'avg_calories': avg_calories,
                        'avg_protein': avg_protein,
                        'total_entries': total_entries,
                        'days_with_entries': days_with_entries,
                    })
                    reminder.metadata = metadata
                    # avoid touching other fields
                    reminder.save(update_fields=['metadata'])

            # Build label using whatever values we now have
            return {
                'source_type': 'personal_data',
                'label': TransparencyLabel.SOURCE_TYPES['personal_data'],
                'short_label': f"Based on your last {days} days",
                'explanation': (
                    "This recommendation is based on your nutrition data "
                    f"from the past {days} days. We analyzed {total_entries or 0} meal logs."
                ),
                'data_points': [
                    f"Average calories: {avg_calories if avg_calories is not None else 'N/A'} kcal/day",
                    f"Average protein: {avg_protein if avg_protein is not None else 'N/A'} g/day",
                    f"Days logged: {days_with_entries if days_with_entries is not None else 'N/A'}",
                ],
            }

        # ---------- PURE GUIDELINE-BASED REMINDERS ----------
        if rtype == 'general':
            return {
                'source_type': 'guidelines',
                'label': TransparencyLabel.SOURCE_TYPES['guidelines'],
                'short_label': "Based on health guidelines",
                'explanation': (
                    "This reminder is based on general health recommendations "
                    "and best practices for maintaining a healthy lifestyle."
                ),
                'data_points': []
            }

        # ---------- DEFAULT / FALLBACK ----------
        return {
            'source_type': 'combined',
            'label': TransparencyLabel.SOURCE_TYPES['combined'],
            'short_label': "Based on your data + health guidelines",
            'explanation': (
                "This recommendation combines your personal health data "
                "with established health guidelines."
            ),
            'data_points': []
        }

    @staticmethod
    def add_transparency_to_reminder(reminder):
        """
        Add transparency metadata to a reminder.
        Called when reminder is created.
        Safe even if the model has no `metadata` field.
        """
        # Start from existing metadata if present, otherwise empty dict
        metadata = getattr(reminder, "metadata", None) or {}

        # Add timestamp
        metadata['created_timestamp'] = timezone.now().isoformat()

        # Add data source info for nutrition reminders
        rtype = getattr(reminder, "reminder_type", None)
        if rtype == 'nutrition':
            from healthdata.models import NutritionEntry
            from django.db.models import Avg, Count

            week_ago = timezone.localdate() - timedelta(days=7)
            entries = NutritionEntry.objects.filter(
                user=reminder.user,
                logged_at__gte=week_ago
            )

            if entries.exists():
                agg = entries.aggregate(
                    avg_calories=Avg('calories'),
                    avg_protein=Avg('protein_g'),
                    total_entries=Count('id'),
                )

                metadata.update({
                    'data_sources_used': ['nutrition'],
                    'days_analyzed': 7,
                    'avg_calories': round(agg['avg_calories'] or 0, 1),
                    'avg_protein': round(float(agg['avg_protein'] or 0), 1),
                    'total_entries': agg['total_entries'],
                    'days_with_entries': entries.values('logged_at').distinct().count(),
                })

        # Only write back if the model actually has a `metadata` field
        if hasattr(reminder, "metadata"):
            reminder.metadata = metadata
            reminder.save()
        else:
            # If there is no metadata field, we just don't persist it.
            # The transparency label will still fall back gracefully.
            pass
