from django.contrib.auth.decorators import login_required, permission_required, user_passes_test
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth.views import LogoutView
from django.http import HttpRequest, HttpResponse, JsonResponse, HttpResponseRedirect
from django.shortcuts import render, redirect, reverse
from django.contrib.auth import authenticate, login, logout
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import TemplateView, CreateView, ListView
from django.views.generic.edit import FormMixin
from random import random
from .models import Profile
from .forms import UploadFileForm
from django.views.decorators.cache import cache_page
from django.utils.translation import gettext_lazy as _, ngettext


# def handle_uploaded_file(f):
#     with open(f'uploads/{f.name}', 'wb+') as destination:
#         for chunk in f.chunks():
#             destination.write(chunk)
#
#
# def upload_file(request):
#     if request.method == 'POST':
#         form = UploadFileForm(request.POST, request.FILES)
#         if form.is_valid():
#             handle_uploaded_file(request.FILES['avatar'])
#
#             return HttpResponseRedirect(reverse_lazy('myauth:about-me'))
#     else:
#         form = UploadFileForm()
#     return render(request, 'myauth/about-me.html', {'form': form})

class HelloView(View):
    welcome_message = _("Hello my world!")

    def get(self, request: HttpRequest) -> HttpResponse:
        items_str = request.GET.get("items") or 0
        items = int(items_str)
        products_line = ngettext(
            "one product",
            "{count} products",
            items,
        )
        products_line = products_line.format(count=items)
        #welcome_message = _("Hello my world!")
        return HttpResponse(
            f"<h1>{self.welcome_message}</h1>"
            f"\n<h2>{products_line}</h2>"
                            )


class AboutMeView(TemplateView, FormMixin):
    template_name = 'myauth/about-me.html'
    form_class = UploadFileForm
    success_url = reverse_lazy('myauth:about-me')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = self.request.user
        context['form'] = self.get_form()
        return context

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        profile, created = Profile.objects.get_or_create(user=self.request.user)
        profile.avatar = form.cleaned_data['avatar']
        profile.bio = form.cleaned_data['bio']
        profile.save()
        return super().form_valid(form)

    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form))


class UsersListView(ListView):
    template_name = 'myauth/users_list.html'
    context_object_name = "users_list"
    queryset = User.objects.all()


class RegisterView(CreateView):
    form_class = UserCreationForm
    template_name = 'myauth/register.html'
    success_url = reverse_lazy('myauth:about-me')

    def form_valid(self, form):
        response = super().form_valid(form)
        Profile.objects.create(user=self.object)
        username = form.cleaned_data.get("username")
        password = form.cleaned_data.get("password1")

        user = authenticate(
            self.request,
            username=username,
            password=password,
        )
        login(request=self.request, user=user)
        return response


class MyLogoutView(View):
    def get(self, request):
        logout(request)
        return redirect('myauth:login')


def user_check(user):
    return lambda u: user.is_superuser


@user_passes_test(user_check, redirect_field_name='myauth:about-me')
def set_cookie_view(request: HttpRequest) -> HttpResponse:
    response = HttpResponse("cookie set")
    response.set_cookie("fizz", "buzz", max_age=3600)
    return response


@cache_page(60 * 2)
def get_cookie_view(request: HttpRequest) -> HttpResponse:
    value = request.COOKIES.get("fizz", "default value")
    return HttpResponse(f"Cookie value: {value!r} + {random()}")


@permission_required('myauth.view_profile', raise_exception=True)
def set_session_view(request: HttpRequest) -> HttpResponse:
    request.session["foobar"] = "spameggs"
    return HttpResponse("session set")


@login_required
def get_session_view(request: HttpRequest) -> HttpResponse:
    value = request.session.get("foobar", "default")
    return HttpResponse(f"Session value: {value!r}")


class FooBarView(View):
    def get(self, request: HttpRequest) -> JsonResponse:
        return JsonResponse({"foo": "bar", "spam": "eggs"})
