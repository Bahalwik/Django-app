from django.core.management import BaseCommand
from shopapp.models import Product, Order


class Command(BaseCommand):
    def handle(self, *args, **options):
        order = Order.objects.first()
        if not order:
            self.stdout.write("no orders")
            return

        products = Product.objects.all()
        for product in products:
            order.products.add(product)

        order.save()
        self.stdout.write(f'Added products {order.products.all()} to order {order}')




