from django.shortcuts import render
from django.views.generic import ListView, CreateView, DetailView
from .models import Article
from django.urls import reverse_lazy, reverse
from django.contrib.syndication.views import Feed


class ArticleListView(ListView):
    queryset = (
        Article.objects
        .filter(pub_date__isnull=False)
        .order_by("-pub_date")

    )
    context_object_name = 'articles'


class ArticleDetailView(DetailView):
    model = Article


class LatestArticlesFeed(Feed):
    title = "Blog articles (latest)"
    description = "Updates on changes and addition blog articles"
    link = reverse_lazy("new_blogapp:articles")

    def items(self):
        return (
            Article.objects
            .filter(pub_date__isnull=False)
            .order_by("-pub_date")[:5]
        )

    def item_title(self, item: Article):
        return item.title

    def item_description(self, item: Article):
        return item.body[:200]

