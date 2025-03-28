from rest_framework import serializers
from .models import Product, Order


class ProductSerializers(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = (
            "pk",
            "name",
            "description",
            "price",
            "discount",
            "created_at",
            "archived",
            "preview",

        )


class OrderSerializers(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = (
            "delivery_adress",
            "promocode",
            "created_at",
            "user",
            "products",
            "receipt",

        )
