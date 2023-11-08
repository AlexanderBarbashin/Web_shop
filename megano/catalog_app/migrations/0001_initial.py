# Generated by Django 4.2.2 on 2023-10-05 17:38

import catalog_app.models
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=50, verbose_name='Название')),
            ],
            options={
                'verbose_name': 'Категория',
                'verbose_name_plural': 'Категории',
            },
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('price', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='Цена')),
                ('count', models.PositiveIntegerField(verbose_name='Остаток')),
                ('date', models.DateTimeField(auto_now_add=True, verbose_name='Дата добавления')),
                ('title', models.CharField(max_length=50, verbose_name='Название')),
                ('description', models.CharField(max_length=200, verbose_name='Описание')),
                ('fullDescription', models.TextField(verbose_name='Полное описание')),
                ('freeDelivery', models.BooleanField(verbose_name='Бесплатная доставка')),
                ('rating', models.DecimalField(decimal_places=1, default=5, max_digits=2, verbose_name='Рейтинг')),
                ('limited', models.BooleanField(verbose_name='Ограниченный тираж')),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='products', to='catalog_app.category', verbose_name='Категория')),
            ],
            options={
                'verbose_name': 'Продукт',
                'verbose_name_plural': 'Продукты',
                'ordering': ['price'],
            },
        ),
        migrations.CreateModel(
            name='Sale',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('salePrice', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='Цена со скидкой')),
                ('dateFrom', models.DateField(verbose_name='Дата начала акции')),
                ('dateTo', models.DateField(verbose_name='Дата окончания акции')),
            ],
            options={
                'verbose_name': 'Скидка',
                'verbose_name_plural': 'Скидки',
            },
        ),
        migrations.CreateModel(
            name='Specification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='Наименование')),
                ('value', models.CharField(max_length=50, verbose_name='Значение')),
            ],
            options={
                'verbose_name': 'Характеристика',
                'verbose_name_plural': 'Характеристики',
            },
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, verbose_name='Имя')),
            ],
            options={
                'verbose_name': 'Тэг',
                'verbose_name_plural': 'Тэги',
            },
        ),
        migrations.CreateModel(
            name='Review',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('author', models.CharField(max_length=150, verbose_name='Автор')),
                ('email', models.EmailField(max_length=254, verbose_name='Электронный адрес')),
                ('text', models.TextField(verbose_name='Текст')),
                ('rate', models.PositiveSmallIntegerField(verbose_name='Оценка')),
                ('date', models.DateTimeField(auto_now_add=True, verbose_name='Дата добавления')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reviews', to='catalog_app.product', verbose_name='Продукт')),
            ],
            options={
                'verbose_name': 'Отзыв',
                'verbose_name_plural': 'Отзывы',
                'ordering': ['-date'],
            },
        ),
        migrations.AddField(
            model_name='product',
            name='sale',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='products', to='catalog_app.sale', verbose_name='Скидка'),
        ),
        migrations.AddField(
            model_name='product',
            name='specifications',
            field=models.ManyToManyField(blank=True, null=True, related_name='products', to='catalog_app.specification', verbose_name='Характеристики'),
        ),
        migrations.AddField(
            model_name='product',
            name='tags',
            field=models.ManyToManyField(blank=True, null=True, related_name='products', to='catalog_app.tag', verbose_name='Тэги'),
        ),
        migrations.CreateModel(
            name='Image',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('src', models.ImageField(upload_to=catalog_app.models.image_directory_path, verbose_name='Ссылка')),
                ('alt', models.CharField(max_length=100, verbose_name='Описание')),
                ('product', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='images', to='catalog_app.product', verbose_name='Продукт')),
            ],
            options={
                'verbose_name': 'Изображение',
                'verbose_name_plural': 'Изображения',
            },
        ),
        migrations.AddField(
            model_name='category',
            name='image',
            field=models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, related_name='category', to='catalog_app.image', verbose_name='Изображение'),
        ),
        migrations.AddField(
            model_name='category',
            name='main_category',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='subcategories', to='catalog_app.category', verbose_name='Главная категория'),
        ),
    ]
