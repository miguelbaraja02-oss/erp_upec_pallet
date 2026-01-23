from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from ..forms import ProfileAvatarForm

@login_required
def upload_avatar(request):
    profile = request.user.profile

    if request.method == "POST":
        form = ProfileAvatarForm(
            request.POST,
            request.FILES,
            instance=profile
        )
        if form.is_valid():
            form.save()
            return redirect("core:welcome")
    else:
        form = ProfileAvatarForm(instance=profile)

    return render(
        request,
        "profile/upload_avatar.html",
        {"form": form}
    )
