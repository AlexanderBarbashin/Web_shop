from django.db import models
from django.db.models import Avg


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
    specifications = models.ManyToManyField(Specification, null=True,
                                            related_name='products', verbose_name='Характеристики')
    rating = models.DecimalField(decimal_places=1, max_digits=2, default=5, verbose_name='Рейтинг')
    limited = models.BooleanField(verbose_name='Ограниченный тираж')
    sale = models.ForeignKey(Sale, null=True, on_delete=models.SET_NULL, related_name='products', verbose_name='Скидка')

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

