from django.contrib.auth.views import LoginView
from django.urls import path
from .views import get_cookie_view, set_cookie_view, set_session_view, get_session_view, MyLogoutView, \
    RegisterView, FooBarView, AboutMeView, UsersListView, HelloView

app_name = "myauth"


urlpatterns = [
    path('login/', LoginView.as_view(
        template_name="myauth/login.html",
        redirect_authenticated_user=True,
        ),
        name='login'
    ),
    path('logout/', MyLogoutView.as_view(), name="logout"),
    path('hello/', HelloView.as_view(), name="hello"),

    path('about-me/', AboutMeView.as_view(), name="about-me"),
    path("users/", UsersListView.as_view(), name='users_list'),
    path('register/', RegisterView.as_view(), name="register"),
    path('cookie/get/', get_cookie_view, name="get_cookie"),
    path('cookie/set/', set_cookie_view, name="cookie_set"),
    path('session/get/', get_session_view, name="get_session"),
    path('session/set/', set_session_view, name="set_session"),
    path('foo-bar/', FooBarView.as_view(), name="foo-bar"),
]