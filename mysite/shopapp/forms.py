from django import forms
from .models import Product, Order
from django.contrib.auth.models import Group
from django.forms import ModelForm


class CSVImportForm(forms.Form):
    csv_file = forms.FileField()


class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            result = [single_file_clean(d, initial) for d in data]
        else:
            result = [single_file_clean(data, initial)]
        return result


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ("name", "price", "description", "discount", "created_by", "preview")
        widgets = {'created_by': forms.HiddenInput()}

    images = MultipleFileField()

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(ProductForm, self).__init__(*args, **kwargs)

    def save(self, commit=True):
        instance = super(ProductForm, self).save(commit=False)
        if self.request and self.request.user:
            instance.created_by = self.request.user
        if commit:
            instance.save()
        return instance


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = "delivery_adress", "promocode", "user", "products"


class GroupForm(ModelForm):
    class Meta:
        model = Group
        fields = ["name", 'permissions']
