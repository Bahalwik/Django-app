"""Набор представлений для ИМа: товары, заказы и т.д."""
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.core.cache import cache
from django.contrib.auth.models import Group
from django.shortcuts import render, redirect, reverse
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect, \
    JsonResponse, Http404
from timeit import default_timer
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import ListView, DetailView, CreateView, \
    UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, \
    PermissionRequiredMixin, UserPassesTestMixin
from .models import Product, Order, ProductImage
from .forms import ProductForm, OrderForm, GroupForm
from rest_framework.viewsets import ModelViewSet
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from .serializers import ProductSerializers, OrderSerializers
from drf_spectacular.utils import extend_schema, OpenApiResponse
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response
from csv import DictWriter
from rest_framework.parsers import MultiPartParser
from .common import save_csv_products
import logging
from django.contrib.syndication.views import Feed
from myauth.models import Profile

log = logging.getLogger(__name__)


class LatestProductsFeed(Feed):
    title = "Products (latest)"
    description = "Updates on changes and addition blog articles"
    link = reverse_lazy("new_blogapp:articles")

    def items(self):
        return (
            Product.objects
            .filter(archived=False)
            .order_by("-created_at")[:5]
        )

    def item_title(self, item: Product):
        return item.name

    def item_description(self, item: Product):
        return item.description[:200]



@extend_schema(description="Order views CRUD")
class OrderViewSet(ModelViewSet):
    """Набор представлений для действий над Order.Полный CRUD для Order."""

    queryset = Order.objects.all()
    serializer_class = OrderSerializers
    filter_backends = [
        SearchFilter,
        DjangoFilterBackend,
        OrderingFilter
    ]
    search_fields = ["delivery_adress", "user", "products"]
    filterset_fields = [

        "delivery_adress",
        "promocode",
        "user",
        "products",
    ]

    ordering_fields = [

        "delivery_adress",
        "promocode",
        "user",
        "products",

    ]

    @extend_schema(
        summary="Get one product by ID",
        description="Retrives **product**, returns 404 if not found",
        responses={
            200: ProductSerializers,
            404: OpenApiResponse(description="Empty response, product by id not found"),
        }
    )
    def retrieve(self, *args, **kwargs):
        return super().retrieve(*args, **kwargs)


class ProductViewSet(ModelViewSet):
    """Набор представлений для действий над Product.Полный CRUD для Product."""

    queryset = Product.objects.all()
    serializer_class = ProductSerializers
    filter_backends = [
        SearchFilter,
        DjangoFilterBackend,
        OrderingFilter
    ]
    search_fields = ["name", "description"]
    filterset_fields = [
        "name",
        "description",
        "price",
        "discount",
        "created_at",
        "archived",
    ]
    ordering_fields = [
        "pk",
        "name",
        "price",
        "discount",

    ]

    #@method_decorator(cache_page(60 * 2))
    def list(self, *args, **kwargs):
        print("hello products list")
        return super().list(*args, **kwargs)

    @action(methods=["get"], detail=False)
    def download_csv(self, request: Request):

        response = HttpResponse(content_type="text/scv")
        filename = "products-export.scv"
        response["Content-Disposition"] = f"attachment; filename{filename}"
        queryset = self.filter_queryset(self.get_queryset())
        fields = [
            "name",
            "description",
            "price",
            "discount",
        ]
        queryset = queryset.only(*fields)
        writer = DictWriter(response, fieldnames=fields)
        writer.writeheader()
        for product in queryset:
            writer.writerow({
                field: getattr(product, field)
                for field in fields
            })

        return response

    @action(
        detail=False,
        methods=["post"],
        parser_classes=[MultiPartParser],
    )
    def upload_csv(self, request: Request):
        products = save_csv_products(
            request.FILES["file"].file,
            encoding=request.encoding,
        )
        serializer = self.get_serializer(products, many=True)
        return Response(serializer.data)


class ShopIndexView(View):
    """Стартовая страница shopapp, с витриной товаров, время работы и текст.

    На "витрине" выведен список из названий товара и его цены.
    """

    def get(self, request: HttpRequest) -> HttpResponse:
        """Метод get."""
        context = {
            "products": Product.objects.all(),
            "time_running": default_timer(),
            "items": 1,
        }

        log.debug("Products for shop index: %s", context)
        log.info("Rendering shop index")
        print("shop index context", context)
        return render(request, 'shopapp/shop-index.html', context=context)


class GroupsListView(View):
    """Создание групп с определёнными правами.

    Показать весь список групп и их права.
    """

    def get(self, request: HttpRequest) -> HttpResponse:
        context = {
            "form": GroupForm(),
            "groups": Group.objects.prefetch_related('permissions').all(),
        }
        return render(request, 'shopapp/groups_list.html', context)

    def post(self, request: HttpRequest):
        form = GroupForm(request.POST)
        if form.is_valid():
            form.save()

        return redirect(request.path)


class ProductDetailsView(DetailView):
    template_name = 'shopapp/product_details.html'
    # model = Product
    queryset = Product.objects.prefetch_related("images")
    context_object_name = 'product'


class ProductListView(ListView):
    template_name = 'shopapp/products_list.html'
    context_object_name = "products"
    queryset = Product.objects.filter(archived=False)


class ProductCreateView(CreateView):
    # def test_func(self):
    #     print(self.request.user.perms)
    #     return self.request.user.is_superuser

    model = Product
    form_class = ProductForm
    success_url = reverse_lazy("shopapp:products_list")

    def get_form_kwargs(self):
      kwargs = super().get_form_kwargs()
      kwargs['request'] = self.request
      return kwargs


class ProductUpdateView(UserPassesTestMixin, UpdateView):
    def test_func(self):
        product = self.get_object()
        if self.request.user.is_superuser or self.request.user == product.created_by:
            return True
        return False

    model = Product
    form_class = ProductForm
    template_name_suffix = "_update_form"

    def get_success_url(self):
        return reverse(
            "shopapp:product_details",
            kwargs={"pk": self.object.pk},
        )

    def form_valid(self, form):
        files = form.cleaned_data["images"]
        for image in files:
            ProductImage.objects.create(
                product=self.object,
                image=image,
            )
        return super().form_valid(form)


class ProductDeleteView(DeleteView):
    model = Product
    success_url = reverse_lazy("shopapp:products_list")

    def form_valid(self, form):
        success_url = self.get_success_url()
        self.object.archived = True
        self.object.save()
        return HttpResponseRedirect(success_url)


class OrderDeleteView(DeleteView):
    model = Order
    success_url = reverse_lazy("shopapp:orders_list")


class OrderCreateView(CreateView):
    model = Order
    form_class = OrderForm
    success_url = reverse_lazy("shopapp:orders_list")


class OrderUpdateView(UpdateView):
    model = Order
    form_class = OrderForm
    template_name_suffix = "_update_form"

    def get_success_url(self):
        return reverse(
            "shopapp:order_details",
            kwargs={"pk": self.object.pk},
        )


class OrdersListView(LoginRequiredMixin, ListView):
    queryset = (
        Order.objects
        .select_related("user")
        .prefetch_related('products')
    )

    context_object_name = 'orders'


class OrderDetailView(PermissionRequiredMixin, DetailView):
    permission_required = "shopapp.view_order"
    queryset = (
        Order.objects
        .select_related("user")
        .prefetch_related('products')
    )
    context_object_name = 'order'


class ProductsDataExportView(View):
    def get(self, request: HttpRequest) -> JsonResponse:

        cache_key = 'products_data_export'
        products_data = cache.get(cache_key)
        if products_data is None:
            products = Product.objects.order_by('pk').all()
            products_data = [
                {
                    "pk": product.pk,
                    "name": product.name,
                    "price": product.price,
                    "archived": product.archived,
                }
                for product in products
            ]
            cache.set(cache_key, products_data, 300)

        return JsonResponse({"products": products_data})


class OrdersExportDataView(View):
    def get(self, request: HttpRequest) -> JsonResponse:
        orders = Order.objects.order_by("pk").all()
        orders_data = [
            {
                "pk": order.pk,
                "delivery_address": order.delivery_adress,
                "promocode": order.promocode,
                "user": order.user.id,
                "products": [
                    [
                        product.id,
                        product.name
                    ]
                    for product in order.products.all()
                ]
            }
            for order in orders
        ]
        return JsonResponse({"orders": orders_data})


class UserOrdersListView(LoginRequiredMixin, ListView):
    template_name = 'shopapp/user_orders_list.html'
    context_object_name = "orders"
    login_url = 'myauth:login'

    def get_queryset(self, **kwargs):
        self.owner = self.kwargs['user_id']
        queryset = Order.objects.filter(user=self.owner)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            user_order_info = Profile.objects.filter(user=self.owner)

            context['user'] = user_order_info[0].user
            return context
        except:
            raise Http404("No User matches the given query.")


class UserOrdersDataExportView(View):
    def get(self, request: HttpRequest, user_id: int) -> JsonResponse:

        cache_key = f'user_{user_id}orders_data_export'

        user_orders_data = cache.get(cache_key)

        if user_orders_data is None:
            user = get_object_or_404(User, id=user_id)

            orders = Order.objects.filter(user=user).order_by('pk').all()

            user_orders_data = [
            {
                "pk": order.pk,
                "delivery_address": order.delivery_adress,
                "promocode": order.promocode,
                "user": order.user.id,
                "products": [
                        product.name
                    for product in order.products.all()
                ]
            }
            for order in orders
        ]
            cache.set(cache_key, user_orders_data, timeout=300)

        return JsonResponse({"orders": user_orders_data})
