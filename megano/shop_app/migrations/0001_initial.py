# Generated by Django 4.2.2 on 2023-11-09 08:18

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("users_app", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("catalog_app", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Basket",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("session_id", models.CharField(max_length=100, null=True)),
            ],
            options={
                "verbose_name": "Корзина",
                "verbose_name_plural": "Корзины",
            },
        ),
        migrations.CreateModel(
            name="DeliveryPrice",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "free_delivery_point",
                    models.DecimalField(
                        decimal_places=2,
                        max_digits=10,
                        verbose_name="Порог бесплатной доставки",
                    ),
                ),
                (
                    "price",
                    models.DecimalField(
                        decimal_places=2, max_digits=10, verbose_name="Стоимость"
                    ),
                ),
            ],
            options={
                "verbose_name": "Стоимость доставки",
                "verbose_name_plural": "Стоимость доставки",
            },
        ),
        migrations.CreateModel(
            name="ExpressDeliveryPrice",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "price",
                    models.DecimalField(
                        decimal_places=2, max_digits=10, verbose_name="Стоимость"
                    ),
                ),
            ],
            options={
                "verbose_name": "Стоимость экспресс доставки",
                "verbose_name_plural": "Стоимость экспресс доставки",
            },
        ),
        migrations.CreateModel(
            name="Order",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "createdAt",
                    models.DateTimeField(
                        auto_now_add=True, verbose_name="Дата создания"
                    ),
                ),
                (
                    "fullName",
                    models.CharField(max_length=150, verbose_name="Полное имя"),
                ),
                (
                    "email",
                    models.EmailField(max_length=254, verbose_name="Электронный адрес"),
                ),
                (
                    "phone",
                    models.PositiveIntegerField(
                        null=True, verbose_name="Номер телефона"
                    ),
                ),
                (
                    "deliveryType",
                    models.CharField(max_length=20, verbose_name="Тип доставки"),
                ),
                (
                    "paymentType",
                    models.CharField(max_length=20, verbose_name="Тип оплаты"),
                ),
                (
                    "totalCost",
                    models.DecimalField(
                        decimal_places=2,
                        max_digits=10,
                        null=True,
                        verbose_name="Итоговая стоимость",
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        default="created", max_length=20, verbose_name="Статус"
                    ),
                ),
                ("city", models.CharField(max_length=50, verbose_name="Город")),
                ("address", models.CharField(max_length=150, verbose_name="Адрес")),
            ],
            options={
                "verbose_name": "Заказ",
                "verbose_name_plural": "Заказы",
                "ordering": ["-createdAt"],
            },
        ),
        migrations.CreateModel(
            name="ProductsInOrderCount",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "count_in_order",
                    models.PositiveSmallIntegerField(
                        default=0, verbose_name="Количество товаров в заказе"
                    ),
                ),
                (
                    "order",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="products_in_order_count",
                        to="shop_app.order",
                        verbose_name="Заказ",
                    ),
                ),
                (
                    "product",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="products_in_order_count",
                        to="catalog_app.product",
                        verbose_name="Товар",
                    ),
                ),
            ],
            options={
                "verbose_name": "Количество товаров в заказе",
                "verbose_name_plural": "Количества товаров в заказе",
            },
        ),
        migrations.CreateModel(
            name="ProductsInBasketCount",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "count_in_basket",
                    models.PositiveSmallIntegerField(
                        default=0, verbose_name="Количество товаров в корзине"
                    ),
                ),
                (
                    "basket",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="products_in_basket_count",
                        to="shop_app.basket",
                        verbose_name="Корзина",
                    ),
                ),
                (
                    "product",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="products_in_basket_count",
                        to="catalog_app.product",
                        verbose_name="Товар",
                    ),
                ),
            ],
            options={
                "verbose_name": "Количество товаров в корзине",
                "verbose_name_plural": "Количества товаров в корзине",
            },
        ),
        migrations.AddField(
            model_name="order",
            name="products",
            field=models.ManyToManyField(
                related_name="orders",
                through="shop_app.ProductsInOrderCount",
                to="catalog_app.product",
                verbose_name="Товары в заказе",
            ),
        ),
        migrations.AddField(
            model_name="order",
            name="profile",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="orders",
                to="users_app.profile",
                verbose_name="Профиль",
            ),
        ),
        migrations.AddField(
            model_name="basket",
            name="products",
            field=models.ManyToManyField(
                related_name="basket",
                through="shop_app.ProductsInBasketCount",
                to="catalog_app.product",
                verbose_name="Товары в корзине",
            ),
        ),
        migrations.AddField(
            model_name="basket",
            name="user",
            field=models.OneToOneField(
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="basket",
                to=settings.AUTH_USER_MODEL,
                verbose_name="Пользователь",
            ),
        ),
    ]
