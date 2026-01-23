from django import forms
from django.contrib.auth import get_user_model
from .models import Profile

User = get_user_model()

class ProfileForm(forms.ModelForm):
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)

    class Meta:
        model = Profile
        fields = ["avatar", "phone", "address", "bio", "first_name", "last_name"]



class ProfileAvatarForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = [
            "avatar",
        ]
