from django.contrib import admin
from django.http import HttpRequest

from shop_app.models import (
    Category,
    Image,
    Tag,
    Review,
    Specification,
    Product,
    Sale,
    Basket,
    Order,
    ExpressDeliveryPrice,
    DeliveryPrice
)


class CategoryAdmin(admin.ModelAdmin):
    """Класс для администрирования модели категории и подкатегории. Родитель: ModelAdmin."""

    list_display = 'pk', 'title', 'image', 'main_category'


class ImageAdmin(admin.ModelAdmin):
    """Класс для администрирования модели изображения. Родитель: ModelAdmin."""

    list_display = 'pk', 'src', 'alt'


class TagAdmin(admin.ModelAdmin):
    """Класс для администрирования модели тэга. Родитель: ModelAdmin."""

    list_display = 'pk', 'name'


class ReviewAdmin(admin.ModelAdmin):
    """Класс для администрирования модели отзыва. Родитель: ModelAdmin."""

    list_display = 'pk', 'author', 'email', 'text', 'rate', 'date', 'product'


class SpecificationAdmin(admin.ModelAdmin):
    """Класс для администрирования модели характеристики. Родитель: ModelAdmin."""

    list_display = 'pk', 'name', 'value'


class ImageInline(admin.StackedInline):
    """Класс для администрирования модели изображения при администрировании модели продукта. Родитель: StackedInline."""

    model = Image
    extra = 1


class SaleAdmin(admin.ModelAdmin):
    """Класс для администрирования модели скидки. Родитель: ModelAdmin."""

    list_display = 'salePrice', 'dateFrom', 'dateTo'


class ProductAdmin(admin.ModelAdmin):
    """Класс для администрирования модели продукта. Родитель: ModelAdmin."""

    list_display = 'pk', 'title', 'category', 'price'
    readonly_fields = 'rating',
    inlines = [ImageInline]


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


admin.site.register(Category, CategoryAdmin)

admin.site.register(Image, ImageAdmin)

admin.site.register(Tag, TagAdmin)

admin.site.register(Review, ReviewAdmin)

admin.site.register(Specification, SpecificationAdmin)

admin.site.register(Sale, SaleAdmin)

admin.site.register(Product, ProductAdmin)

admin.site.register(Basket, BasketAdmin)

admin.site.register(Order, OrderAdmin)

admin.site.register(DeliveryPrice, DeliveryPriceAdmin)

admin.site.register(ExpressDeliveryPrice, ExpressDeliveryPriceAdmin)
