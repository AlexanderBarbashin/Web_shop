# Generated by Django 4.2.2 on 2023-09-09 07:35

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('shop_app', '0005_productsinbasketcount'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='basket',
            name='products',
        ),
        migrations.RemoveField(
            model_name='basket',
            name='profile',
        ),
        migrations.AddField(
            model_name='basket',
            name='user',
            field=models.OneToOneField(default=1, on_delete=django.db.models.deletion.PROTECT, related_name='basket', to=settings.AUTH_USER_MODEL, verbose_name='Пользователь'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='productsinbasketcount',
            name='prods_count',
            field=models.PositiveSmallIntegerField(default=0, verbose_name='Количество товаров в корзине'),
        ),
    ]
