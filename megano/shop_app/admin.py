from django.contrib import admin

from shop_app.models import Category, Image, Tag, Review, Specification, Product, Sale, Basket


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
    list_display = 'pk', 'profile'

admin.site.register(Category, CategoryAdmin)

admin.site.register(Image, ImageAdmin)

admin.site.register(Tag, TagAdmin)

admin.site.register(Review, ReviewAdmin)

admin.site.register(Specification, SpecificationAdmin)

admin.site.register(Sale, SaleAdmin)

admin.site.register(Product, ProductAdmin)

admin.site.register(Basket, BasketAdmin)