from django.shortcuts import render
from django.views.generic import ListView, CreateView, DetailView
from django.urls import reverse_lazy
from .forms import ArticlesForm
from .models import Article


class ArticleListView(ListView):
    queryset = (
        Article.objects
        .select_related("author", 'category')
        .prefetch_related('tags')

    )
    context_object_name = 'articles'


class ArticleCreateView(CreateView):
    model = Article
    form_class = ArticlesForm
    success_url = reverse_lazy("blogapp:articles_list")
