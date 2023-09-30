# Generated by Django 4.2.2 on 2023-09-16 07:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop_app', '0015_remove_order_products_productsinordercount'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='products',
            field=models.ManyToManyField(related_name='orders', through='shop_app.ProductsInOrderCount', to='shop_app.product', verbose_name='Товары в заказе'),
        ),
    ]