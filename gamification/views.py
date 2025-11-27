from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .services import GamificationService
from .models import Badge, UserBadge


@login_required
def rewards_dashboard(request):
    """Display the rewards/progress page"""
    service = GamificationService(request.user)
    stats = service.get_user_stats()

    # Get ALL badges with earned status
    all_badges = Badge.objects.all()
    earned_badge_ids = set(UserBadge.objects.filter(user=request.user).values_list('badge_id', flat=True))

    all_badges_data = []
    for badge in all_badges:
        is_earned = badge.id in earned_badge_ids
        user_badge = None
        if is_earned:
            user_badge = UserBadge.objects.filter(user=request.user, badge=badge).first()

        all_badges_data.append({
            'badge': badge,
            'earned': is_earned,
            'user_badge': user_badge,
            'earned_at': user_badge.earned_at if user_badge else None,
        })

    context = {
        'current_streak': stats['current_streak'],
        'longest_streak': stats['longest_streak'],
        'total_activities': stats['total_activities'],
        'earned_badges': stats['earned_badges'],
        'total_badges': stats['total_badges'],
        'earned_badge_count': stats['earned_badge_count'],
        'weekly_progress': stats['weekly_progress'],
        'all_badges': all_badges_data,
    }

    return render(request, 'gamification/rewards_dashboard.html', context)


@login_required
def get_gamification_stats(request):
    """AJAX endpoint to get current stats"""
    service = GamificationService(request.user)
    stats = service.get_user_stats()

    earned_badges_data = [
        {
            'id': badge.badge.id,
            'name': badge.badge.name,
            'icon': badge.badge.icon,
            'earned_at': badge.earned_at.isoformat(),
        }
        for badge in stats['earned_badges']
    ]

    weekly_progress_data = None
    if stats['weekly_progress']:
        wp = stats['weekly_progress']
        weekly_progress_data = {
            'week_start': wp.week_start.isoformat(),
            'days_completed': wp.days_completed,
            'goal_target': wp.goal_target,
            'progress_percentage': wp.progress_percentage,
            'is_complete': wp.is_complete,
        }

    return JsonResponse({
        'current_streak': stats['current_streak'],
        'longest_streak': stats['longest_streak'],
        'total_activities': stats['total_activities'],
        'earned_badges': earned_badges_data,
        'total_badges': stats['total_badges'],
        'earned_badge_count': stats['earned_badge_count'],
        'weekly_progress': weekly_progress_data,
    })