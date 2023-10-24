from datetime import datetime

from django.db.models import Count, Sum, Q, QuerySet
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import permissions, status
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.generics import ListAPIView, RetrieveAPIView, CreateAPIView
from rest_framework.request import Request
from rest_framework.response import Response

from catalog_app.models import Category, Tag, Product, Review
from catalog_app.serializers import (
    CategorySerializer,
    TagSerializer,
    ProductListSerializer,
    ProductSaleSerializer,
    ProductDetailsSerializer,
    ReviewSerializer
)
from catalog_app.utils import ProductListViewPagination, ProductListFilter, SaleListViewPagination, request_handler


class CategoryView(ListAPIView):
    """Представление категорий и подкатегорий товаров. Родитель: ListAPIView."""

    queryset = Category.objects.filter(main_category=None).prefetch_related('subcategories').\
        prefetch_related('products').annotate(prods_count=Count('products')).annotate(subcats_count=Count('subcategories')).filter(Q(prods_count__gt=0) | Q(subcats_count__gt=0))
    # queryset = Category.objects.filter(main_category=None).prefetch_related('subcategories')
    serializer_class = CategorySerializer


class TagsView(ListAPIView):
    """Представление тэгов товаров. Родитель: ListAPIView."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class ProductListView(ListAPIView):
    """Представление списка товаров. Родитель: ListAPIView."""

    queryset = Product.objects.all().select_related('category').prefetch_related('images').prefetch_related('tags').\
        prefetch_related('reviews').annotate(product_reviews=Count('reviews'))
    serializer_class = ProductListSerializer
    pagination_class = ProductListViewPagination
    filter_backends = [
        SearchFilter,
        DjangoFilterBackend,
        OrderingFilter
    ]
    filterset_class = ProductListFilter
    ordering_fields = ['rating', 'price', 'product_reviews', 'date']
    search_fields = ['title']

    def get(self, request: Request, *args) -> Response:
        """Метод для получения списка товаров."""

        _mutable = request.query_params._mutable
        request.query_params._mutable = True
        request = request_handler(request)
        request.query_params._mutable = _mutable
        return super().get(request, *args)


class ProductPopularListView(ListAPIView):
    """Представление списка топ-товаров. Родитель: ListAPIView."""

    queryset = Product.objects.filter(count__gt=0).select_related('category').prefetch_related('images').\
                   prefetch_related('tags').prefetch_related('reviews').prefetch_related('products_in_order_count').\
                   annotate(purchase_count=Sum(
        'products_in_order_count__count_in_order',
        filter=Q(products_in_order_count__order__status='paid'))).order_by('-rating', '-purchase_count')[:5]
    serializer_class = ProductListSerializer


class ProductLimitedListView(ListAPIView):
    """Представление списка товаров из серии 'ограниченный тираж'. Родитель: ListAPIView."""

    queryset = Product.objects.filter(count__gt=0).filter(limited=True).select_related('category').\
                   prefetch_related('images').prefetch_related('tags').prefetch_related('reviews').\
                   order_by('-rating')[:5]
    serializer_class = ProductListSerializer


class ProductSaleListView(ListAPIView):
    """Представление списка товаров со скидками. Родитель: ListAPIView."""

    today = datetime.now().date()
    queryset = Product.objects.filter(count__gt=0).select_related('sale').filter(sale__dateFrom__lte=today).\
        filter(sale__dateTo__gte=today).prefetch_related('images').order_by('sale__salePrice')
    serializer_class = ProductSaleSerializer
    pagination_class = SaleListViewPagination


class BannerListView(ListAPIView):
    """Представление банеров с товарами из избранных категорий. Родитель: ListAPIView."""

    serializer_class = ProductListSerializer

    def get_queryset(self) -> QuerySet:
        """Метод для получения QuerySet из самых дешевых товаров в избранных категориях."""

        categories = Category.objects.prefetch_related('products').filter(products__count__gt=0).order_by('?')[:5]
        products_in_banners_list = [
            Product.objects.select_related('category').filter(category=category, count__gt=0). \
                order_by('price')[:1][0].id
            for category
            in categories
        ]
        queryset = Product.objects.filter(id__in=products_in_banners_list).select_related('category'). \
            prefetch_related('images').prefetch_related('tags').prefetch_related('reviews')
        return queryset


class ProductDetailView(RetrieveAPIView):
    """Представление детальной страницы товара. Родитель: RetrieveAPIView."""

    queryset = Product.objects.select_related('category').prefetch_related('images').prefetch_related('tags').\
        prefetch_related('reviews').prefetch_related('specifications')
    serializer_class = ProductDetailsSerializer


class ProductReviewCreate(CreateAPIView):
    """Представление добавления отзыва о товаре. Родитель: CreateAPIView."""

    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticated]


    def create(self, request: Request, *args, **kwargs) -> Response:
        """Метод для создания отзыва от товаре."""

        product_pk = kwargs['pk']
        request.data['product'] = product_pk
        super().create(request, *args, **kwargs)
        reviews = Review.objects.select_related('product').filter(product=product_pk)
        reviews_serializer = ReviewSerializer(reviews, many=True)
        return Response(reviews_serializer.data, status=status.HTTP_200_OK)
