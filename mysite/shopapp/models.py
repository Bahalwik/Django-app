

from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.urls import reverse


def product_preview_directory_path(instance: "Product", filename: str) -> str:
    return "products/product_{pk}/preview/{filename}".format(
        pk=instance.name,
        filename=filename
    )


class Product(models.Model):
    """
    Модель представляет товар, который можно продавать в интернет магазине

    Заказы: :model:`shopapp.Order`
    """
    class Meta:
        ordering = ["name"]
        verbose_name = _("Product")
        verbose_name_plural = _("Products")

    name = models.CharField(max_length=100, db_index=True)
    description = models.TextField(null=False, blank=True, db_index=True)
    price = models.DecimalField(default=0, max_digits=8, decimal_places=2)
    discount = models.SmallIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    archived = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, blank=True, null=True)
    preview = models.ImageField(null=True, blank=True, upload_to=product_preview_directory_path)

    def __str__(self):
        return f"Product(pk={self.pk}, name={self.name!r})"

    def get_absolute_url(self):
        return reverse("shopapp:product_details", kwargs={"pk": self.pk})


class Order(models.Model):
    class Meta:
        verbose_name = _("Order")
        verbose_name_plural = _("Orders")

    delivery_adress = models.TextField(null=True, blank=True)
    promocode = models.CharField(max_length=30, null=False, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    products = models.ManyToManyField(Product, related_name="orders")
    receipt = models.FileField(null=True, upload_to='orders/receipts/')


def product_images_directory_path(instance: "ProductImage", filename: str) -> str:
    return "products/product_{pk}/images/{filename}".format(
        pk=instance.product.name,
        filename=filename
    )


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to=product_images_directory_path)
    description = models.CharField(max_length=200, null=False, blank=True)
