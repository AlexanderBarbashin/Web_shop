# Generated by Django 4.2.2 on 2023-09-12 15:31

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("shop_app", "0009_alter_order_phone"),
    ]

    operations = [
        migrations.AlterField(
            model_name="order",
            name="totalCost",
            field=models.DecimalField(
                decimal_places=2,
                max_digits=10,
                null=True,
                verbose_name="Итоговая стоимость",
            ),
        ),
    ]
