from django import forms
from .models import Article


class ArticlesForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = "title", "content", "author", "category", 'tags'
