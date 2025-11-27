from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from .models import Avatar, UserProfile


@login_required
def avatar_select(request):
    """Avatar selection view"""
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    avatars = Avatar.objects.all()

    if request.method == "POST":
        avatar_id = request.POST.get("avatar_id")
        if avatar_id:
            avatar = get_object_or_404(Avatar, pk=avatar_id)
            profile.avatar = avatar
            profile.save()
        # Redirect to the root URL which will handle the redirect properly
        return redirect('/')  # ← CHANGED THIS LINE

    context = {
        "avatars": avatars,
        "current_avatar": profile.avatar,
    }
    return render(request, "motivation/avatar_select.html", context)