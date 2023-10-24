from django.contrib.auth.models import User
from django.db import models

from catalog_app.models import Product
from users_app.models import Profile


class Basket(models.Model):
    """Модель корзины с товарами. Родитель: Model."""

    user = models.OneToOneField(User, null=True, on_delete=models.PROTECT, related_name='basket',
                                verbose_name='Пользователь')
    session_id = models.CharField(null=True, max_length=100)
    products = models.ManyToManyField(Product, through='ProductsInBasketCount', related_name='basket',
                                      verbose_name='Товары в корзине')

    def __str__(self) -> str:
        """Метод для вывода названия корзины."""

        username = self.user.username if self.user else 'Anonym'
        return 'Корзина пользователя {username}'.format(
            username=username
        )

    class Meta:
        verbose_name = 'Корзина'
        verbose_name_plural = 'Корзины'


class ProductsInBasketCount(models.Model):
    """Модель количества товаров в корзине. Родитель: Model."""

    basket = models.ForeignKey(Basket, on_delete=models.CASCADE, related_name='products_in_basket_count',
                               verbose_name='Корзина')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='products_in_basket_count',
                                verbose_name='Товар')
    count_in_basket = models.PositiveSmallIntegerField(default=0, verbose_name='Количество товаров в корзине')

    def __str__(self) -> str:
        """Метод для вывода количества товаров в корзине в качестве названия модели."""

        username = self.basket.user.username if self.basket.user else 'Anonym'
        return 'Количество товаров {product} в корзине пользователя {username}: {count}'.format(
            product=self.product,
            username=username,
            count=self.count_in_basket
        )

    class Meta:
        verbose_name = 'Количество товаров в корзине'
        verbose_name_plural = 'Количества товаров в корзине'


class Order(models.Model):
    """Модель заказа. Родитель: Model."""

    createdAt = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    fullName = models.CharField(max_length=150, verbose_name='Полное имя')
    email = models.EmailField(verbose_name='Электронный адрес')
    phone = models.PositiveIntegerField(null=True, verbose_name='Номер телефона')
    deliveryType = models.CharField(max_length=20, verbose_name='Тип доставки')
    paymentType = models.CharField(max_length=20, verbose_name='Тип оплаты')
    totalCost = models.DecimalField(decimal_places=2, max_digits=10, null=True, verbose_name='Итоговая стоимость')
    status = models.CharField(max_length=20, default='created', verbose_name='Статус')
    city = models.CharField(max_length=50, verbose_name='Город')
    address = models.CharField(max_length=150, verbose_name='Адрес')
    products = models.ManyToManyField(Product, through='ProductsInOrderCount', related_name='orders',
                                      verbose_name='Товары в заказе')
    profile = models.ForeignKey(Profile, null=True, on_delete=models.PROTECT, related_name='orders',
                                verbose_name='Профиль')

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'
        ordering = ['-createdAt']


class ProductsInOrderCount(models.Model):
    """Модель количества товаров в заказе. Родитель: Model."""

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='products_in_order_count',
                              verbose_name='Заказ')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='products_in_order_count',
                                verbose_name='Товар')
    count_in_order = models.PositiveSmallIntegerField(default=0, verbose_name='Количество товаров в заказе')

    class Meta:
        verbose_name = 'Количество товаров в заказе'
        verbose_name_plural = 'Количества товаров в заказе'


class DeliveryPrice(models.Model):
    """Модель стоимости доставки. Родитель: Model."""

    free_delivery_point = models.DecimalField(decimal_places=2, max_digits=10, verbose_name='Порог бесплатной доставки')
    price = models.DecimalField(decimal_places=2, max_digits=10, verbose_name='Стоимость')

    class Meta:
        verbose_name = 'Стоимость доставки'
        verbose_name_plural = 'Стоимость доставки'


class ExpressDeliveryPrice(models.Model):
    """Модель стоимости экспресс доставки. Родитель: Model."""

    price = models.DecimalField(decimal_places=2, max_digits=10, verbose_name='Стоимость')

    class Meta:
        verbose_name = 'Стоимость экспресс доставки'
        verbose_name_plural = 'Стоимость экспресс доставки'