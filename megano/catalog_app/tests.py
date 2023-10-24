import json
from datetime import datetime

from django.contrib.auth.models import User
from django.db.models import Count, Q, Sum
from django.urls import reverse

from rest_framework.test import APITestCase

from catalog_app.models import Category, Tag, Product, Review, Image
from users_app.models import Profile


def fixture_recode(fixture_name: str) -> str:
    """Функция для перекодирования фикстуры в формат 'utf-8'."""

    recoded_fixture_name = fixture_name[:-5] + '-recoded.json'
    with open('catalog_app/fixtures/{fixture_name}'.format(
        fixture_name=fixture_name
    ), encoding='utf-16') as f:
        data = json.load(f)
    with open('catalog_app/fixtures/{recoded_fixture_name}'.format(
        recoded_fixture_name=recoded_fixture_name
    ), 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False)
    return recoded_fixture_name


class CategoryViewTestCase(APITestCase):
    """Тест представления cписка категорий товаров. Родитель: APITestCase."""

    fixtures = [
        fixture_recode('tags-fixture.json'),
        fixture_recode('specifications-fixture.json'),
        fixture_recode('products-fixture.json'),
        fixture_recode('images-fixture.json'),
        fixture_recode('categories-fixture.json')
    ]

    def test_categories_view(self) -> None:
        """Метод для тестирования получения списка категорий товаров."""

        response = self.client.get(
            reverse('categories')
        )
        recieved_data = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertQuerySetEqual(
            qs=Category.objects.filter(main_category=None).prefetch_related('subcategories').\
        prefetch_related('products').annotate(prods_count=Count('products')).\
                annotate(subcats_count=Count('subcategories')).filter(Q(prods_count__gt=0) | Q(subcats_count__gt=0)),
            values=(category['id'] for category in recieved_data),
            transform=lambda category: category.id,
            ordered=False
        )

class TagsViewTestCase(APITestCase):
    """Тест представления cписка тэгов товаров. Родитель: APITestCase."""

    fixtures = [
        fixture_recode('tags-fixture.json')
    ]

    def test_tags_view(self) -> None:
        """Метод для тестирования получения списка тэгов товаров."""

        response = self.client.get(
            reverse('tags')
        )
        recieved_data = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertQuerySetEqual(
            qs=Tag.objects.all(),
            values=(tag['id'] for tag in recieved_data),
            transform=lambda tag: tag.id,
            ordered=False
        )

class ProductListViewTestCase(APITestCase):
    """Тесты представлений cписков товаров. Родитель: APITestCase."""

    fixtures = [
        fixture_recode('images-fixture.json'),
        fixture_recode('tags-fixture.json'),
        fixture_recode('specifications-fixture.json'),
        fixture_recode('categories-fixture.json'),
        fixture_recode('sales-fixture.json'),
        fixture_recode('products-fixture.json')
    ]

    def test_products_list_view(self) -> None:
        """Метод для тестирования получения списка товаров."""

        response = self.client.get(
            reverse('catalog'),
        )
        recieved_data = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertQuerySetEqual(
            qs=Product.objects.filter(count__gt=0).select_related('category').prefetch_related('images').\
                   prefetch_related('tags').prefetch_related('reviews').annotate(product_reviews=Count('reviews')).\
                   order_by('price')[:4],
            values=(product['id'] for product in recieved_data['items']),
            transform=lambda product: product.id,
            ordered=False
        )

    def test_products_popular_view(self) -> None:
        """Метод для тестирования получения списка популярных товаров."""

        response = self.client.get(
            reverse('products_popular'),
        )
        recieved_data = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertQuerySetEqual(
            qs=Product.objects.filter(count__gt=0).select_related('category').prefetch_related('images').\
                   prefetch_related('tags').prefetch_related('reviews').prefetch_related('products_in_order_count').\
                   annotate(purchase_count=Sum(
        'products_in_order_count__count_in_order',
        filter=Q(products_in_order_count__order__status='paid'))).order_by('-rating', '-purchase_count')[:5],
            values=(product['id'] for product in recieved_data),
            transform=lambda product: product.id,
            ordered=False
        )

    def test_products_limited_view(self) -> None:
        """Метод для тестирования получения списка товаров с ограниченным тиражом."""

        response = self.client.get(
            reverse('products_limited'),
        )
        recieved_data = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertQuerySetEqual(
            qs=Product.objects.filter(count__gt=0).filter(limited=True).select_related('category').\
                   prefetch_related('images').prefetch_related('tags').prefetch_related('reviews').\
                   order_by('-rating')[:5],
            values=(product['id'] for product in recieved_data),
            transform=lambda product: product.id,
            ordered=False
        )

    def test_products_sale_view(self) -> None:
        """Метод для тестирования получения списка товаров со скидками."""

        response = self.client.get(
            reverse('products_sales'),
        )
        recieved_data = json.loads(response.content)
        today = datetime.now().date()
        self.assertEqual(response.status_code, 200)
        self.assertQuerySetEqual(
            qs=Product.objects.filter(count__gt=0).select_related('sale').filter(sale__dateFrom__lte=today).\
                filter(sale__dateTo__gte=today).prefetch_related('images').order_by('sale__salePrice')[:3],
            values=(product['id'] for product in recieved_data['items']),
            transform=lambda product: product.id,
            ordered=False
        )

    def test_products_in_banner_view(self) -> None:
        """Метод для тестирования получения баннеров с товарами из избранных категорий."""

        response = self.client.get(
            reverse('product_banners')
        )
        categories = Category.objects.prefetch_related('products').filter(products__count__gt=0).order_by('?')[:5]
        products_in_banners_list = [
            Product.objects.select_related('category').filter(category=category, count__gt=0). \
                order_by('price')[:1][0].id
            for category
            in categories
        ]
        recieved_data = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertQuerySetEqual(
            qs=Product.objects.filter(id__in=products_in_banners_list).select_related('category').\
        prefetch_related('images').prefetch_related('tags').prefetch_related('reviews'),
            values=(product['id'] for product in recieved_data),
            transform=lambda product: product.id,
        )


class ProductDetailViewTestCase(APITestCase):
    """Тест представления детальной информации о товаре. Родитель: APITestCase."""

    fixtures = [
        fixture_recode('images-fixture.json'),
        fixture_recode('tags-fixture.json'),
        fixture_recode('specifications-fixture.json'),
        fixture_recode('categories-fixture.json'),
        fixture_recode('sales-fixture.json'),
        fixture_recode('products-fixture.json')
    ]

    def test_product_details_view(self) -> None:
        """Метод для тестирования получения детальной информации о товаре."""

        product = Product.objects.first()
        response = self.client.get(
            reverse(
                'product',
                kwargs={'pk': product.pk}
            )
        )
        recieved_data = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(recieved_data['id'], product.id)
        self.assertContains(response, product.title)


class ProductReviewCreateTestCase(APITestCase):
    """Тест представления добавления отзыва о товаре. Родитель: APITestCase."""

    @classmethod
    def setUpClass(cls) -> None:
        """Метод для предварительной подготовки БД к проведению теста."""

        cls.credentials = dict(username='test_user', password='test_password')
        cls.user = User.objects.create_user(**cls.credentials)
        cls.profile = Profile.objects.create(
            user=cls.user,
            fullName='test_name',
        )
        cls.image = Image.objects.create()
        cls.category = Category.objects.create(
            title='test_category_title',
            image=cls.image
        )
        cls.product = Product.objects.create(
            category=cls.category,
            price=100,
            count=1,
            title='test_product_title',
            description='test_description',
            fullDescription='test_fullDescription',
            freeDelivery=False,
            limited=False
        )

    @classmethod
    def tearDownClass(cls) -> None:
        """Метод для очистки БД после проведения теста."""

        cls.user.delete()
        cls.profile.delete()
        cls.product.delete()
        cls.category.delete()
        cls.image.delete()


    def setUp(self) -> None:
        """Метод для предварительной подготовки БД к проведению теста."""

        self.review_text = 'test_review_text'
        Review.objects.filter(text=self.review_text).delete()
        self.client.login(**self.credentials)

    def test_product_review_create(self) -> None:
        """Метод для тестирования добавления отзыва о товаре."""

        response = self.client.post(
            reverse(
                'review_create',
                kwargs={'pk': self.product.pk}
            ),
            {
                'author': 'test_author',
                'email': 'test@email.ru',
                'text': 'test_review_text',
                'rate': 5
            }
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Review.objects.filter(text=self.review_text).exists())
        self.assertContains(response, self.review_text)

    def test_product_review_create_not_authenticated(self) -> None:
        """Метод для тестирования добавления отзыва о товаре неаутентифицированным пользователем."""

        self.client.logout()
        response = self.client.post(
            reverse(
                'review_create',
                kwargs={'pk': self.product.pk}
            ),
            {
                'author': 'test_author',
                'email': 'test@email.ru',
                'text': 'test_review_text',
                'rate': 5
            }
        )
        self.assertEqual(response.status_code, 403)
