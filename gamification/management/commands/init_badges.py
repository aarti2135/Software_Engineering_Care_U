from django.core.management.base import BaseCommand
from gamification.models import Badge


class Command(BaseCommand):
    help = 'Initialize default badges in the database'

    def handle(self, *args, **options):
        badges_data = [
            {
                'badge_type': 'first_log',
                'name': 'First Log',
                'description': 'Logged your first activity',
                'icon': '🌟',
                'requirement': 1,
            },
            {
                'badge_type': 'week_streak',
                'name': '7-Day Streak',
                'description': 'Logged activities for 7 consecutive days',
                'icon': '🔥',
                'requirement': 7,
            },
            {
                'badge_type': 'month_streak',
                'name': '30-Day Streak',
                'description': 'Logged activities for 30 consecutive days',
                'icon': '🚀',
                'requirement': 30,
            },
            {
                'badge_type': 'data_master',
                'name': 'Data Master',
                'description': 'Logged 100 activities in total',
                'icon': '📈',
                'requirement': 100,
            },
            {
                'badge_type': 'goal_achiever',
                'name': 'Goal Achiever',
                'description': 'Completed your first goal',
                'icon': '🎯',
                'requirement': 1,
            },
            {
                'badge_type': 'consistent',
                'name': 'Consistency Champion',
                'description': 'Achieved a 14-day longest streak',
                'icon': '💎',
                'requirement': 14,
            },
        ]

        created_count = 0
        updated_count = 0

        for badge_data in badges_data:
            badge, created = Badge.objects.update_or_create(
                badge_type=badge_data['badge_type'],
                defaults={
                    'name': badge_data['name'],
                    'description': badge_data['description'],
                    'icon': badge_data['icon'],
                    'requirement': badge_data['requirement'],
                }
            )

            if created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f'✓ Created badge: {badge.name}'))
            else:
                updated_count += 1
                self.stdout.write(self.style.WARNING(f'⟳ Updated badge: {badge.name}'))

        self.stdout.write(
            self.style.SUCCESS(
                f'\n✅ Complete! Created {created_count} new, updated {updated_count} existing.'
            )
        )