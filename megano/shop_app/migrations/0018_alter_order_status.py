# Generated by Django 4.2.2 on 2023-09-17 09:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop_app', '0017_rename_prods_count_productsinbasketcount_count_in_basket_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.CharField(default='created', max_length=20, verbose_name='Статус'),
        ),
    ]