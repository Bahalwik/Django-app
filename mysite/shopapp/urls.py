from django.urls import path, include
from rest_framework.routers import DefaultRouter
from django.views.decorators.cache import cache_page

from .views import ShopIndexView, GroupsListView, ProductDetailsView\
    , ProductListView, OrdersListView, OrderDetailView, ProductCreateView, ProductUpdateView, \
            ProductDeleteView, OrderCreateView, OrderUpdateView, OrderDeleteView, OrdersExportDataView, \
    ProductViewSet, OrderViewSet, LatestProductsFeed, ProductsDataExportView, UserOrdersListView,\
    UserOrdersDataExportView

app_name = "shopapp"

routers = DefaultRouter()
routers.register("products", ProductViewSet)
routers.register("orders", OrderViewSet)

urlpatterns = [

    path("", cache_page(60 * 3)(ShopIndexView.as_view()), name='index'),

    path("api/", include(routers.urls)),

    path("groups/", GroupsListView.as_view(), name="groups_list"),
    path("products/", ProductListView.as_view(), name='products_list'),
    path("products/create/", ProductCreateView.as_view(), name='product_create'),
    path("products/<int:pk>/", ProductDetailsView.as_view(), name='product_details'),
    path("products/<int:pk>/update/", ProductUpdateView.as_view(), name='product_update'),
    path("products/<int:pk>/archive/", ProductDeleteView.as_view(), name='product_delete'),
    path("products/latest/feed/", LatestProductsFeed(), name='products_feed'),
    path("products/export/", ProductsDataExportView.as_view(), name="products_export"),

    path("orders/", OrdersListView.as_view(), name='orders_list'),
    path("orders/export/", OrdersExportDataView.as_view(), name="order_export"),
    path("orders/create-order/", OrderCreateView.as_view(), name='create_order'),
    path("orders/<int:pk>/", OrderDetailView.as_view(), name='order_details'),
    path("orders/<int:pk>/update", OrderUpdateView.as_view(), name='order_update'),
    path("orders/<int:pk>/delete", OrderDeleteView.as_view(), name='order_delete'),

    path("orders/user/<int:user_id>/", UserOrdersListView.as_view(), name='order_user'),
    path("orders/user/<int:user_id>/export/", UserOrdersDataExportView.as_view(), name='order_user_export'),
]
