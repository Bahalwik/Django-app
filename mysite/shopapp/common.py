from csv import DictReader
from io import TextIOWrapper

from shopapp.models import Product, Order


def save_csv_products(file, encoding):
    csv_file = TextIOWrapper(
        file,
        encoding=encoding,
    )

    reader = DictReader(csv_file)

    products = [
        Product(**row)
        for row in reader
    ]
    Product.objects.bulk_create(products)
    return products


def save_csv_orders(file, encoding):
    csv_file = TextIOWrapper(
        file,
        encoding=encoding,
    )

    reader = DictReader(csv_file)

    chars = [',', ' ']
    for _row in reader:
        pr = filter(lambda i: i not in chars, _row['products'])

        order = Order(
            delivery_adress=_row['delivery_adress'],
            promocode=_row['promocode'],
            user_id=_row['user'],
        )
        order.save()
        order.products.set(map(int, pr))

    return order
