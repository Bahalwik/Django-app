from django import forms
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.core.exceptions import ValidationError


class UserBioForm(forms.Form):
    name = forms.CharField(label="Your name", max_length=50)
    age = forms.IntegerField(label="Your age", min_value=1, max_value=100)
    bio = forms.CharField(label="Biography", widget=forms.Textarea)


def validate_file_size(file: InMemoryUploadedFile) -> None:
    if file and file.size > 1048576:
        raise ValidationError("file size > 1Mb")


class UploadFileForm(forms.Form):
    file = forms.FileField(validators=[validate_file_size])

