from string import ascii_letters
from random import choices
from django.conf import settings
from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from shopapp.models import Product, Order



class ProductDetailsViewTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.product = Product.objects.create(name="Best product")

    @classmethod
    def tearDownClass(cls):
        cls.product.delete()

    def test_get_product(self):
        self.client.get(
            reverse("shopapp:product_details", kwargs={"pk": self.product.pk})
        )

    def test_get_product_and_check_content(self):
        response = self.client.get(
            reverse("shopapp:product_details", kwargs={"pk": self.product.pk})
        )
        self.assertContains(response, self.product.name)


class ProductsListViewTestCase(TestCase):
    fixtures = [
        'products-fixture.json',
        'users-fixture.json',
        'orders-fixture.json',
        ]

    def test_product(self):
        response = self.client.get(reverse("shopapp:products_list"))
        products = Product.objects.filter(archived=False).all()
        products_ = response.context["products"]

        for product in Product.objects.filter(archived=False).all():
            self.assertContains(response, product.name)

        for p, p_ in zip(products, products_):
            self.assertEqual(p.pk, p_.pk)

        self.assertQuerysetEqual(
            qs=Product.objects.filter(archived=False).all(),
            values=(p.pk for p in response.context["products"]),
            transform=lambda p: p.pk
        )
        self.assertTemplateUsed(response, "shopapp/products_list.html")


class OrderListViewTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        #cls.credentials = dict()
        cls.user = User.objects.create_user(username="test", password="testing123")

    @classmethod
    def tearDownClass(cls):
        cls.user.delete()

    def setUp(self) -> None:
        self.client.force_login(self.user)

    def test_orders_view(self):
        response = self.client.get(reverse("shopapp:orders_list"))
        self.assertContains(response, "Orders")

    def test_orders_view_not_authenticated(self):
        self.client.logout()
        response = self.client.get(reverse("shopapp:orders_list"))
        self.assertEqual(response.status_code, 302)
        self.assertIn(str(settings.LOGIN_URL), response.url)


class OrderDetailsViewTestCase(TestCase):
    fixtures = [
            "products-fixture.json",
        ]

    @classmethod
    def setUpClass(cls):
        cls.user = User.objects.create_user(username="test", password="testing123")
        cls.user.user_permissions.add(29, 32)

    @classmethod
    def tearDownClass(cls):
        cls.user.delete()

    def setUp(self) -> None:
        self.client.force_login(self.user)
        self.order = Order.objects.create(
            delivery_adress="Test order",
            promocode='Test promo',
            user=self.user
            )

    def tearDown(self) -> None:
        self.order.delete()

    def test_order_details_and_check(self):

        response = self.client.get(
            reverse("shopapp:order_details", kwargs={"pk": self.order.pk})
        )
        self.assertContains(response, self.order.promocode)
        self.assertContains(response, self.order.delivery_adress)
        self.assertContains(response, self.order.pk)


class OrdersExportTestCase(TestCase):
    fixtures = [
       'users-fixture.json',
       'products-fixture.json',
       'orders-fixture.json',
    ]

    @classmethod
    def setUpClass(cls):
        cls.user = User.objects.create_user(username="test",
                                            password="testing123",
                                            is_staff=True)
        cls.user.user_permissions.add(29, 30, 31, 32)

    @classmethod
    def tearDownClass(cls):
        cls.user.delete()

    def setUp(self) -> None:
        self.client.force_login(self.user)

    def test_export_orders(self):
        response = self.client.get(reverse("shopapp:order_export"))
        self.assertEqual(response.status_code, 200)
        orders = Order.objects.order_by("pk").all()

        expected_data = [
            {
                "pk": order.pk,
                "delivery_address": order.delivery_address,
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

        order_data = response.json()
        self.assertEqual(order_data['orders'], expected_data)
