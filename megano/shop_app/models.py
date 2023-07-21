from django.db import models


class Category(models.Model):
    title = models.CharField(max_length=50, verbose_name='Название')
    main_category = models.BooleanField(verbose_name='Главная категория')



class Image(models.Model):
    pass


class Tag(models.Model):
    pass


class Specification(models.Model):
    pass


class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name='products', verbose_name='Категория')
    price = models.DecimalField(decimal_places=2, max_digits=10, verbose_name='Цена')
    count = models.PositiveIntegerField(verbose_name='Остаток')
    date = models.DateTimeField(auto_now_add=True, verbose_name='Дата добавления')
    title = models.CharField(max_length=50, verbose_name='Название')
    description = models.CharField(max_length=200, verbose_name='Описание')
    fullDescription = models.TextField(verbose_name='Полное описание')
    freeDelivery = models.BooleanField(verbose_name='Бесплатная доставка')
    tags = models.ManyToManyField(Tag, related_name='products', verbose_name='Тэги')
    specifications = models.ManyToManyField(Specification, related_name='products', verbose_name='Характеристики')
    rating = models.DecimalField(decimal_places=1, max_digits=3, default=0, verbose_name='Рейтинг')


class Review(models.Model):
    pass

