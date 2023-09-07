from django.db.models import Q, QuerySet
from django_filters.rest_framework import FilterSet
from django_filters import NumberFilter, BooleanFilter, CharFilter

from shop_app.models import Product, Category


class ProductListFilter(FilterSet):
    """Фильтр списка продуктов. Родитель: FilterSet."""

    minPrice = NumberFilter(field_name='price', lookup_expr='gte')
    maxPrice = NumberFilter(field_name='price', lookup_expr='lte')
    freeDelivery = BooleanFilter(field_name='freeDelivery', method='filter_free_delivery')
    available = BooleanFilter(field_name='count', method='filter_available')
    tags = CharFilter(field_name='tags', method='filter_tags')
    category = NumberFilter(field_name='category', method='filter_category')

    def filter_free_delivery(self, queryset: QuerySet, name: str, value: bool) -> QuerySet:
        """Метод для фильтрации продуктов с бесплатной доставкой."""

        if value:
            queryset = queryset.filter(freeDelivery=True)
        return queryset

    def filter_available(self, queryset: QuerySet, name: str, value: bool) -> QuerySet:
        """Метод для фильтрации продуктов, доступных для покупки."""

        if value:
            queryset = queryset.filter(count__gt=0)
        return queryset

    def filter_tags(self, queryset: QuerySet, name: str, value: str) -> QuerySet:
        """Метод для фильтрации продуктов по тэгам."""

        if value:
            tags_list = [int(tag) for tag in value if tag.isdigit()]
            for tag in tags_list:
                queryset = queryset.filter(tags=tag)
        return queryset

    def filter_category(self, queryset: QuerySet, name: str, value: str) -> QuerySet:
        """Метод для фильтрации продуктов по категориям."""

        category = Category.objects.get(pk=value)
        if not category.main_category:
            categories_list = Category.objects.filter(Q(main_category=category) | Q(pk=value))
        else:
            categories_list = Category.objects.filter(pk=value)
        queryset = queryset.filter(category__in=categories_list)
        return queryset

    class Meta:
        model = Product
        fields = ['minPrice', 'maxPrice', 'freeDelivery', 'available', 'tags', 'category']
