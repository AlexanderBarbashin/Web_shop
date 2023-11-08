# Generated by Django 4.2.2 on 2023-09-07 18:04

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop_app', '0004_alter_review_options_basket'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProductsInBasketCount',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('prods_count', models.PositiveSmallIntegerField(verbose_name='Количество товаров в корзине')),
                ('basket', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='products_in_basket_count', to='shop_app.basket', verbose_name='Корзина')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='products_in_basket_count', to='shop_app.product', verbose_name='Товар')),
            ],
            options={
                'verbose_name': 'Количество товаров в корзине',
                'verbose_name_plural': 'Количества товаров в корзине',
            },
        ),
    ]
