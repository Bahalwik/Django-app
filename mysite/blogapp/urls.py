from django.urls import path
from .views import ArticleListView, ArticleCreateView

app_name = "blogapp"

urlpatterns = [
    path("articles/", ArticleListView.as_view(), name='articles_list'),
    path("articles/create", ArticleCreateView.as_view(), name='create_articles'),
]
