from django.core.management import BaseCommand
from shopapp.models import Product


class Command(BaseCommand):

    def handle(self, *args, **options):
        self.stdout.write('Create products')

        products_names = [
            ("Laptop",  999),
            ("Desktop", 1999),
            ("Smartphone", 2555),
        ]
        for products_name in products_names:
            product, created = Product.objects.get_or_create(name=products_name[0], price=products_name[1])
            self.stdout.write(f'Create product {product.name}')

        self.stdout.write(self.style.SUCCESS('Products create'))

