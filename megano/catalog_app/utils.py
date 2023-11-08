from catalog_app.models import Category, Product
from django.db.models import Q, QuerySet
from django_filters import BooleanFilter, CharFilter, NumberFilter
from django_filters.rest_framework import FilterSet
from rest_framework.pagination import PageNumberPagination
from rest_framework.request import Request
from rest_framework.response import Response


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


class ProductListViewPagination(PageNumberPagination):
    """Пагинатор списка товаров. Родитель: PageNumberPagination."""
    page_size = 4
    page_query_param = 'currentPage'

    def get_paginated_response(self, data: dict) -> Response:
        """Метод для получения списка товаров, разделенного постранично."""

        last_page_number = self.page.paginator.num_pages
        return Response(
            {
                'items': data,
                'currentPage': self.page.number,
                'lastPage': last_page_number
            }
        )


class SaleListViewPagination(ProductListViewPagination):
    """Пагинатор списка товаров со скидками. Родитель: ProductListViewPagination."""

    page_size = 3


def request_handler(request: Request) -> Request:
    """Функция для приведения параметров запроса поиска товаров в соответствие полям фильтров"""
    if not 'search' in request.query_params:
        request.query_params['search'] = request.query_params.get('filter[name]', '')
    if not 'minPrice' in request.query_params:
        request.query_params['minPrice'] = int(request.query_params.get('filter[minPrice]', 1))
    if not 'maxPrice' in request.query_params:
        request.query_params['maxPrice'] = int(request.query_params.get('filter[maxPrice]', 50000))
    if not 'freeDelivery' in request.query_params:
        request.query_params['freeDelivery'] = request.query_params.get('filter[freeDelivery]', False)
    if not 'available' in request.query_params:
        request.query_params['available'] = request.query_params.get('filter[available]', True)
    if not 'ordering' in request.query_params:
        query_sort_type = request.query_params.get('sortType', 'inc')
        if query_sort_type == 'dec':
            sort_type = '-'
        else:
            sort_type = ''
        request.query_params['ordering'] = '{sort_type}{sort}'.format(
            sort_type=sort_type,
            sort=request.query_params.get('sort', 'price')
        ).replace(
            'reviews', 'product_reviews'
        )
    if not 'tags' in request.query_params:
        request.query_params['tags'] = request.query_params.getlist('tags[]')
    return request