from django.contrib.auth.models import User
from django.core.management import BaseCommand
from shopapp.models import Order, Product
from typing import Sequence
from django.db import transaction


class Command(BaseCommand):
    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write("Create Order")

        user = User.objects.get(username="admin")
        products: Sequence[Product] = Product.objects.all()
        order, created = Order.objects.get_or_create(
            delivery_adress='Piskarevskui dom 5',
            promocode='Sale10',
            user=user
        )
        for product in products:
            order.products.add(product)

        order.save()

        self.stdout.write(f"Created order {order}")
