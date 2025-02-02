from django import forms
from django.contrib.auth.models import User

from .models import Profile


class UploadFileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ("bio", 'avatar',)


