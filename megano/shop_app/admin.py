from django.contrib import admin
from django.http import HttpRequest

from shop_app.models import (
    Basket,
    Order,
    ExpressDeliveryPrice,
    DeliveryPrice
)


class BasketAdmin(admin.ModelAdmin):
    """Класс для администрирования модели корзины. Родитель: ModelAdmin."""

    list_display = 'pk', 'user'


class OrderAdmin(admin.ModelAdmin):
    """Класс для администрирования модели заказа. Родитель: ModelAdmin."""

    list_display = 'pk', 'totalCost'


class DeliveryPriceAdmin(admin.ModelAdmin):
    """Класс для администрирования модели стоимости доставки. Родитель: ModelAdmin."""

    list_display = 'pk', 'free_delivery_point', 'price'

    def has_add_permission(self, request: HttpRequest) -> bool:
        """Метод для обеспечения невозможности создания второго экземпляра модели."""

        return not DeliveryPrice.objects.exists()


class ExpressDeliveryPriceAdmin(admin.ModelAdmin):
    """Класс для администрирования модели стоимости экспресс доставки. Родитель: ModelAdmin."""

    list_display = 'pk', 'price'

    def has_add_permission(self, request: HttpRequest) -> bool:
        """Метод для обеспечения невозможности создания второго экземпляра модели."""

        return not ExpressDeliveryPrice.objects.exists()


admin.site.register(Basket, BasketAdmin)

admin.site.register(Order, OrderAdmin)

admin.site.register(DeliveryPrice, DeliveryPriceAdmin)

admin.site.register(ExpressDeliveryPrice, ExpressDeliveryPriceAdmin)
