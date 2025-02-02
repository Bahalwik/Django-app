import os.path

from django.core.files.storage import FileSystemStorage
from django.shortcuts import render
from .forms import UserBioForm, UploadFileForm
from django.http import HttpRequest, HttpResponse


def process_get_view(request: HttpRequest) -> HttpResponse:
    context = {

    }

    return render(request, "requestdataapp/request-query-params.html", context=context)


def user_form(request: HttpRequest) -> HttpResponse:
    context = {
        "form": UserBioForm(),
    }
    return render(request, "requestdataapp/user-bio-form.html", context)


def handle_file_upload(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            myfile = form.cleaned_data["file"]
            fs = FileSystemStorage()
            filename = fs.save(myfile.name, myfile)
            print("saved file", filename)
    else:
        form = UploadFileForm()
    context = {
        "form": form,
    }
    return render(request, "requestdataapp/file-upload.html", context=context)
