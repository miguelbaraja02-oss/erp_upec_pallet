from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from ..forms import ProfileForm

@login_required
def auth_profile(request):
    profile = request.user.profile
    user = request.user

    if request.method == "POST":
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            profile = form.save(commit=False)
            user.first_name = form.cleaned_data["first_name"]
            user.last_name = form.cleaned_data["last_name"]
            user.save()
            profile.save()
    else:
        form = ProfileForm(
            instance=profile,
            initial={
                "first_name": user.first_name,
                "last_name": user.last_name,
            }
        )

    return render(request, "profile/profile.html", {"form": form})

