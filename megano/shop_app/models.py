from django.contrib.auth.models import User
from django.db import models
from django.db.models import Avg
from users_app.models import Profile


def image_directory_path(instance: 'Image', filename: str) -> str:
    """Функция для формирования директории, в которую сохраняются изображения продуктов и категорий продуктов."""
    return 'shop_app_images/{instance}/{filename}'.format(
        instance=instance,
        filename=filename
    )


class Image(models.Model):
    """Модель изображения. Родитель: Model."""

    src = models.ImageField(
        upload_to=image_directory_path,
        verbose_name='Ссылка'
    )
    alt = models.CharField(max_length=100, verbose_name='Описание')
    product = models.ForeignKey('Product', null=True, blank=True, on_delete=models.CASCADE,
                                related_name='images', verbose_name='Продукт')

    def __str__(self) -> str:
        """Метод для вывода описания изображения в качестве названия изображения."""

        return self.alt

    class Meta:
        verbose_name = 'Изображение'
        verbose_name_plural = 'Изображения'


class Category(models.Model):
    """Модель категории и подкатегории товаров. Родитель: Model."""

    title = models.CharField(max_length=50, verbose_name='Название')
    image = models.OneToOneField(Image, on_delete=models.PROTECT,
                                 related_name='category', verbose_name='Изображение')
    main_category = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE,
                                      related_name='subcategories', verbose_name='Главная категория')

    def __str__(self) -> str:
        """Метод для вывода заголовка категории и подкатегории в качестве названия категории и подкатегории."""

        return self.title

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'


class Tag(models.Model):
    """Модель тэга продукта. Родитель: Model."""

    name = models.CharField(max_length=50, verbose_name='Имя')

    def __str__(self) -> str:
        """Метод для вывода имени тэга в качестве названия тэга."""

        return self.name

    class Meta:
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'


class Specification(models.Model):
    """Модель характеристики продукта. Родитель: Model."""

    name = models.CharField(max_length=100, verbose_name='Наименование')
    value = models.CharField(max_length=50, verbose_name='Значение')

    def __str__(self) -> str:
        """Метод для вывода имени характеристики в качестве названия характеристки."""

        return self.name

    class Meta:
        verbose_name = 'Характеристика'
        verbose_name_plural = 'Характеристики'


class Sale(models.Model):
    """Модель скидки на продукт. Родитель: Model."""

    salePrice = models.DecimalField(decimal_places=2, max_digits=10, verbose_name='Цена со скидкой')
    dateFrom = models.DateField(verbose_name='Дата начала акции')
    dateTo = models.DateField(verbose_name='Дата окончания акции')

    def __str__(self) -> str:
        """Метод для вывода цены продукта со скидкой в качестве названия скидки."""

        return str(self.salePrice)

    class Meta:
        verbose_name = 'Скидка'
        verbose_name_plural = 'Скидки'


class Product(models.Model):
    """Модель продукта. Родитель: Model."""

    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name='products', verbose_name='Категория')
    price = models.DecimalField(decimal_places=2, max_digits=10, verbose_name='Цена')
    count = models.PositiveIntegerField(verbose_name='Остаток')
    date = models.DateTimeField(auto_now_add=True, verbose_name='Дата добавления')
    title = models.CharField(max_length=50, verbose_name='Название')
    description = models.CharField(max_length=200, verbose_name='Описание')
    fullDescription = models.TextField(verbose_name='Полное описание')
    freeDelivery = models.BooleanField(verbose_name='Бесплатная доставка')
    tags = models.ManyToManyField(Tag, null=True, blank=True, related_name='products', verbose_name='Тэги')
    specifications = models.ManyToManyField(Specification, null=True, blank=True,
                                            related_name='products', verbose_name='Характеристики')
    rating = models.DecimalField(decimal_places=1, max_digits=2, default=5, verbose_name='Рейтинг')
    limited = models.BooleanField(verbose_name='Ограниченный тираж')
    sale = models.ForeignKey(Sale, null=True, blank=True, on_delete=models.SET_NULL,
                             related_name='products', verbose_name='Скидка')

    def __str__(self) -> str:
        """Метод для вывода заголовка продукта в качестве названия продукта."""

        return self.title

    class Meta:
        verbose_name = 'Продукт'
        verbose_name_plural = 'Продукты'
        ordering = ['price']


class Review(models.Model):
    """Модель отзыва на продукт. Родитель: Model."""

    author = models.CharField(max_length=150, verbose_name='Автор')
    email = models.EmailField(verbose_name='Электронный адрес')
    text = models.TextField(verbose_name='Текст')
    rate = models.PositiveSmallIntegerField(verbose_name='Оценка')
    date = models.DateTimeField(auto_now_add=True, verbose_name='Дата добавления')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews', verbose_name='Продукт')

    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        ordering = ['-date']

    def save(self, **kwargs) -> None:
        """Метод для пересчета рейтинга продукта при добавлении нового отзыва на продукт."""

        super().save(**kwargs)
        product = self.product
        rating = Review.objects.select_related('product').filter(product=product).aggregate(
            Avg('rate')
        )
        product.rating = rating['rate__avg']
        product.save(update_fields=['rating'])


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
