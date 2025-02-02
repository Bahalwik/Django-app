from django.contrib import admin
from django.db.models import QuerySet
from django.http import HttpRequest, HttpResponse
from shopapp.models import Product, Order, ProductImage
from .common import save_csv_products, save_csv_orders
from .forms import CSVImportForm
from django.shortcuts import render, redirect
from django.urls import path





class OrderInline(admin.TabularInline):
    model = Product.orders.through


class ProductInline(admin.StackedInline):
    model = ProductImage


@admin.action(description="Archive Products")
def mark_archived(modeladmin: admin.ModelAdmin, request: HttpRequest, queryset: QuerySet):
    queryset.update(archived=True)


@admin.action(description="Unarchive Products")
def mark_unarchived(modeladmin: admin.ModelAdmin, request: HttpRequest, queryset: QuerySet):
    queryset.update(archived=False)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    change_list_template = "shopapp/products_changelist.html"
    inlines = [
        OrderInline,
        ProductInline,
    ]
    actions = [
        mark_archived,
        mark_unarchived,
    ]
    list_display = "pk", "name", "description_short", "price", "discount", "archived"
    list_display_links = "pk", "name"
    ordering = "name", "pk"
    search_fields = "name", "description"
    fieldsets = [
        (None, {
            "fields": ("name", "description"),
        }),
        ("Price options", {
            "fields": ("price", "discount"),
            "classes": ("wide", "collapse"),
        }),
        ("Extra options", {
            "fields": ("archived",),
            "classes": ("collapse",),
            "description": "Extra options. Soft delete",

        }),
        ("Created by", {
            "fields": ("created_by",),
            "classes": ("collapse",),
        }),
        ("Images", {
            "fields": ("preview",),
        }),

    ]

    def description_short(self, obj: Product):
        if len(obj.description) < 48:
            return obj.description
        return obj.description[:48] + '...'

    def import_csv(self, request: HttpRequest) -> HttpResponse:
        if request.method == "GET":
            form = CSVImportForm()
            context = {
                "form": form,
            }
            return render(request, "admin/csv_form.html", context)
        form = CSVImportForm(request.POST, request.FILES)
        if not form.is_valid():
            context = {
                form: form
            }
            return render(request, "admin/csv_form.html", context, status=400)

        save_csv_products(
            file=form.files["csv_file"].file,
            encoding=request.encoding,
        )

        self.message_user(request, "Data form csv was imported")
        return redirect("..")

    def get_urls(self):
        urls = super().get_urls()
        new_urls = [
            path(
                "import-products-csv/",
                self.import_csv,
                name="import_products_csv"
            ),
        ]
        return new_urls + urls


class ProductInline(admin.TabularInline):
    model = Order.products.through


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    change_list_template = "shopapp/order_changelist.html"
    inlines = [
        ProductInline,
    ]

    list_display = "delivery_adress", "created_at", "promocode", "user_verbose"

    def get_queryset(self, request):
        return Order.objects.select_related("user")

    def user_verbose(self, obj: Order):
        return obj.user.first_name or obj.user.username

    def import_csv(self, request: HttpRequest) -> HttpResponse:
        if request.method == "GET":
            form = CSVImportForm()
            context = {
                "form": form,
            }
            return render(request, "admin/csv_form.html", context)

        form = CSVImportForm(request.POST, request.FILES)
        if not form.is_valid():
            context = {
                form: form
            }
            return render(request, "admin/csv_form.html", context, status=400)

        save_csv_orders(
            file=form.files["csv_file"].file,
            encoding=request.encoding,
        )

        self.message_user(request, "Data form csv was imported")
        return redirect("..")

    def get_urls(self):
        urls = super().get_urls()
        new_urls = [
            path(
                "import_orders_csv/",
                self.import_csv,
                name="import_orders_csv"
            ),
        ]
        return new_urls + urls
