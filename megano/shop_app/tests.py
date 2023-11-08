import json
import os

from catalog_app.models import Category, Image, Product
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APITestCase
from shop_app.models import Basket, DeliveryPrice, Order, ProductsInBasketCount
from users_app.models import Profile

from megano import settings
from megano.celery import app


class BasketViewTestCase(APITestCase):
    """Тесты представления корзины с товарами. Родитель: APITestCase."""

    @classmethod
    def setUpClass(cls) -> None:
        """Метод для предварительной подготовки БД к проведению теста."""

        cls.credentials = dict(username="test_user", password="test_password")
        cls.user = User.objects.create_user(**cls.credentials)
        product_image = os.path.join(
            settings.MEDIA_ROOT / "catalog_app_images", "test_product.jpg"
        )
        cls.image = Image.objects.create(src=product_image)
        cls.category = Category.objects.create(
            title="test_category_title", image=cls.image
        )
        cls.product = Product.objects.create(
            category=cls.category,
            price=100,
            count=1,
            title="test_product_title",
            description="test_description",
            fullDescription="test_fullDescription",
            freeDelivery=False,
            limited=False,
        )
        cls.basket = Basket.objects.create(user=cls.user)
        cls.products_in_basket_count = ProductsInBasketCount.objects.create(
            basket=cls.basket, product=cls.product, count_in_basket=cls.product.count
        )

    @classmethod
    def tearDownClass(cls) -> None:
        """Метод для очистки БД после проведения теста."""

        cls.basket.delete()
        cls.user.delete()
        cls.product.delete()
        cls.category.delete()
        cls.image.delete()

    def setUp(self) -> None:
        """Метод для предварительной подготовки БД к проведению теста."""

        self.client.login(**self.credentials)

    def test_get_products_in_basket(self) -> None:
        """Метод для тестирования получения списка продуктов в корзине пользователя."""

        response = self.client.get(reverse("basket"))
        recieved_data = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertQuerySetEqual(
            qs=Product.objects.all(),
            values=({product["id"]: product["count"]} for product in recieved_data),
            transform=lambda product: {product.id: product.count},
        )

    def test_add_product_to_basket(self) -> None:
        """Метод для тестирования добавления продуктов в корзину пользователя."""

        product_id = self.product.id
        response = self.client.post(reverse("basket"), {"id": product_id, "count": 1})
        self.product.count += 1
        self.product.save(update_fields=["count"])
        recieved_data = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertQuerySetEqual(
            qs=Product.objects.all(),
            values=({product["id"]: product["count"]} for product in recieved_data),
            transform=lambda product: {product.id: product.count},
        )

    def test_delete_product_from_basket(self) -> None:
        """Метод для тестирования удаления продуктов из корзины пользователя."""

        product_id = self.product.id
        response = self.client.delete(reverse("basket"), {"id": product_id, "count": 1})
        recieved_data = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(recieved_data, [])


class OrderCreateViewTestCase(APITestCase):
    """Тест представления создания заказов. Родитель: APITestCase."""

    @classmethod
    def setUpClass(cls) -> None:
        """Метод для предварительной подготовки БД к проведению теста."""

        Order.objects.all().delete()
        cls.image = Image.objects.create(
            src=os.path.join(
                settings.MEDIA_ROOT / "catalog_app_images", "test_product.jpg"
            )
        )
        cls.category = Category.objects.create(
            title="test_category_title", image=cls.image
        )
        cls.product = Product.objects.create(
            category=cls.category,
            price=100,
            count=1,
            title="test_product_title",
            description="test_description",
            fullDescription="test_fullDescription",
            freeDelivery=False,
            limited=False,
        )

    @classmethod
    def tearDownClass(cls) -> None:
        """Метод для очистки БД после проведения теста."""

        cls.product.delete()
        cls.category.delete()
        cls.image.delete()

    def test_order_create(self) -> None:
        """Метод для тестирования создания заказа."""

        response = self.client.post(
            reverse("orders"),
            [
                {
                    "id": self.product.id,
                    "category": {
                        "title": self.product.category.title,
                        "image": {
                            "src": os.path.join(
                                settings.MEDIA_ROOT / "catalog_app_images",
                                "test_product.jpg",
                            ),
                            "alt": "test_category_image",
                        },
                        "subcategories": [],
                    },
                    "price": self.product.price,
                    "count": self.product.count,
                    "date": self.product.date,
                    "title": self.product.title,
                    "description": self.product.description,
                    "freeDelivery": self.product.freeDelivery,
                    "images": [
                        {
                            "src": os.path.join(
                                settings.MEDIA_ROOT / "catalog_app_images",
                                "test_product.jpg",
                            ),
                            "alt": "test_image",
                        }
                    ],
                    "tags": [],
                    "reviews": [],
                    "rating": 5.0,
                }
            ],
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Order.objects.exists())


class OrderListViewTestCase(APITestCase):
    """Тест представления списка заказов. Родитель: APITestCase."""

    @classmethod
    def setUpClass(cls) -> None:
        """Метод для предварительной подготовки БД к проведению теста."""

        cls.credentials = dict(username="test_user", password="test_password")
        cls.user = User.objects.create_user(**cls.credentials)
        cls.profile = Profile.objects.create(
            user=cls.user,
            fullName="test_name",
        )
        cls.order = Order.objects.create(profile=cls.profile)

    @classmethod
    def tearDownClass(cls) -> None:
        """Метод для очистки БД после проведения теста."""

        cls.order.delete()
        cls.user.delete()

    def setUp(self) -> None:
        """Метод для предварительной подготовки БД к проведению теста."""

        self.client.login(**self.credentials)

    def test_get_orders_list(self) -> None:
        """Метод для тестирования получения списка заказов."""

        response = self.client.get(reverse("orders"))
        recieved_data = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertQuerySetEqual(
            qs=Order.objects.select_related("profile").filter(profile=self.profile),
            values=(order["id"] for order in recieved_data),
            transform=lambda order: order.id,
        )


class OrderDetailViewTestCase(APITestCase):
    """Тест представления детальной страницы заказа. Родитель: APITestCase."""

    @classmethod
    def setUpClass(cls) -> None:
        """Метод для предварительной подготовки БД к проведению теста."""

        cls.credentials = dict(username="test_user", password="test_password")
        cls.user = User.objects.create_user(**cls.credentials)
        cls.profile = Profile.objects.create(
            user=cls.user,
            fullName="test_name",
        )
        cls.order = Order.objects.create(profile=cls.profile)
        cls.image = Image.objects.create(
            src=os.path.join(
                settings.MEDIA_ROOT / "catalog_app_images", "test_product.jpg"
            )
        )
        cls.category = Category.objects.create(
            title="test_category_title", image=cls.image
        )
        cls.product = Product.objects.create(
            category=cls.category,
            price=100,
            count=1,
            title="test_product_title",
            description="test_description",
            fullDescription="test_fullDescription",
            freeDelivery=False,
            limited=False,
        )
        cls.order.products.add(cls.product)
        cls.delivery_price = DeliveryPrice.objects.create(
            free_delivery_point=2000.00, price=200.00
        )

    @classmethod
    def tearDownClass(cls) -> None:
        """Метод для очистки БД после проведения теста."""

        cls.order.delete()
        cls.user.delete()
        cls.product.delete()
        cls.category.delete()
        cls.image.delete()
        cls.delivery_price.delete()

    def setUp(self) -> None:
        """Метод для предварительной подготовки БД к проведению теста."""

        self.client.login(**self.credentials)

    def test_get_order_detail(self) -> None:
        """Метод для тестирования получения детальной информации о заказе."""

        response = self.client.get(
            reverse("order_detail", kwargs={"pk": self.order.pk})
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.order.profile.fullName)

    def test_order_confirm(self) -> None:
        """Метод для тестирования подтверждения заказа."""

        response = self.client.post(
            reverse("order_detail", kwargs={"pk": self.order.pk}),
            {
                "id": self.order.id,
                "createdAt": self.order.createdAt,
                "fullName": "test_name",
                "email": "test@email.ru",
                "phone": "1234567890",
                "deliveryType": "free",
                "paymentType": "online",
                "totalCost": 100.00,
                "status": "created",
                "city": "test_city",
                "address": "test_address",
                "products": [
                    {
                        "id": self.product.id,
                        "category": {
                            "title": self.product.category.title,
                            "image": {
                                "src": os.path.join(
                                    settings.MEDIA_ROOT / "catalog_app_images",
                                    "test_product.jpg",
                                ),
                                "alt": "test_category_image",
                            },
                            "subcategories": [],
                        },
                        "price": self.product.price,
                        "count": self.product.count,
                        "date": self.product.date,
                        "title": self.product.title,
                        "description": self.product.description,
                        "freeDelivery": self.product.freeDelivery,
                        "images": [
                            {
                                "src": os.path.join(
                                    settings.MEDIA_ROOT / "catalog_app_images",
                                    "test_product.jpg",
                                ),
                                "alt": "test_image",
                            }
                        ],
                        "tags": [],
                        "reviews": [],
                        "rating": 5.0,
                    }
                ],
            },
        )
        self.assertEqual(response.status_code, 200)


class PaymentViewTestCase(APITestCase):
    """Тест представления оплаты заказа. Родитель: APITestCase."""

    @classmethod
    def setUpClass(cls) -> None:
        """Метод для предварительной подготовки БД к проведению теста."""

        cls.order = Order.objects.create()

    @classmethod
    def tearDownClass(cls) -> None:
        """Метод для очистки БД после проведения теста."""

        cls.order.delete()

    def setUp(self) -> None:
        """Метод для предварительной подготовки celery к проведению теста."""

        app.conf.task_always_eager = True

    def tearDown(self) -> None:
        """Метод для возвращения celery к прежним настройкам после проведения теста."""

        app.conf.task_always_eager = False

    def test_payment(self) -> None:
        """Метод для тестирования оплаты заказа."""

        response = self.client.post(
            reverse("payment", kwargs={"pk": self.order.pk}),
            {
                "number": 2222222222222222,
                "name": "Test name",
                "month": 12,
                "year": 25,
                "code": 123,
            },
        )
        self.assertEqual(response.status_code, 200)

    def test_payment_not_complete(self) -> None:
        """Метод для тестирования оплаты заказа с нечетным номером карты."""

        response = self.client.post(
            reverse("payment", kwargs={"pk": self.order.pk}),
            {
                "number": 1111111111111111,
                "name": "Test name",
                "month": 12,
                "year": 25,
                "code": 123,
            },
        )
        self.assertEqual(response.status_code, 400)
