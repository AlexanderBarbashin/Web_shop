from datetime import datetime

from django.db.models import Count, Avg

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, permissions
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.generics import ListAPIView
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView


from shop_app.utils import ProductListFilter, ProductListViewPagination, SaleListViewPagination
from shop_app.models import Category, Product, Tag
from shop_app.serializers import CategorySerializer, TagSerializer, ReviewSerializer, \
    ProductDetailsSerializer, ProductListSerializer, ProductSaleSerializer, BannerProductListSerializer, \
    ProductAddToBasketSerializer


class CategoryView(APIView):
    """Представление категорий и подкатегорий товаров. Родитель: APIView."""

    def get(self, request: Request) -> Response:
        """Метод для получения категорий и подкатегорий товаров."""

        categories = Category.objects.filter(main_category=None).prefetch_related('subcategories')
        serializer = CategorySerializer(categories, many=True)
        return Response(serializer.data)


class TagsView(APIView):
    """Представление тэгов товаров. Родитель: APIView."""

    def get(self, request: Request) -> Response:
        """Метод для получения тэгов товаров."""

        tags = Tag.objects.all()
        serializer = TagSerializer(tags, many=True)
        return Response(serializer.data)


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
        if not 'search' in request.query_params:
            request.query_params['search'] = request.query_params.get('filter[title]', '')
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
                sort_type=''
            request.query_params['ordering'] = '{sort_type}{sort}'.format(
                sort_type=sort_type,
                sort=request.query_params.get('sort', 'price')
            ).replace(
                'reviews', 'product_reviews'
            )
        if not 'tags' in request.query_params:
            request.query_params['tags'] = request.query_params.getlist('tags[]')
        request.query_params._mutable = _mutable
        return super().get(request, *args)


class ProductPopularListView(APIView):
    """Представление списка топ-товаров. Родитель: APIView."""

    def get(self, request: Request) -> Response:
        """Метод для получения списка топ-товаров."""

        popular_poducts = Product.objects.filter(count__gt=0).select_related('category').prefetch_related('images').\
                              prefetch_related('tags').prefetch_related('reviews').order_by('-rating')[:5]

        serializer = ProductListSerializer(popular_poducts, many=True)
        return Response(serializer.data)


class ProductLimitedListView(APIView):
    """Представление списка товаров из серии 'ограниченный тираж'. Родитель: APIView."""

    def get(self, request: Request) -> Response:
        """Метод для получения списка товаров из серии 'ограниченный тираж'."""

        limited_poducts = Product.objects.filter(count__gt=0).filter(limited=True).select_related('category').\
            prefetch_related('images').prefetch_related('tags').prefetch_related('reviews').order_by('-rating')[:5]
        serializer = ProductListSerializer(limited_poducts, many=True)
        return Response(serializer.data)


class ProductSaleListView(ListAPIView):
    """Представление списка товаров со скидками. Родитель: ListAPIView."""

    today = datetime.now().date()
    queryset = Product.objects.filter(count__gt=0).select_related('sale').filter(sale__dateFrom__lte=today).\
        filter(sale__dateTo__gte=today).prefetch_related('images').order_by('sale__salePrice')
    serializer_class = ProductSaleSerializer
    pagination_class = SaleListViewPagination


class BannerListView(APIView):
    """Представление банеров с товарами из избранных категорий. Родитель: APIView."""

    def get(self, request):
        """Метод для получения самых дешевых товаров из избранных категорий."""

        categories = Category.objects.prefetch_related('products').filter(products__count__gt=0).\
                         order_by('?')[:5]
        products_in_banners_list = [
            Product.objects.select_related('category').filter(category=category, count__gt=0).\
                order_by('price')[:1][0].id
            for category
            in categories
        ]
        products = Product.objects.filter(id__in=products_in_banners_list).select_related('category').\
            prefetch_related('images').prefetch_related('tags').prefetch_related('reviews')
        serializer = BannerProductListSerializer(products, many=True)
        return Response(serializer.data)


class ProductDetailView(APIView):
    """Представление детальной страницы товара. Родитель: APIView."""

    def get(self, request: Request, **kwargs) -> Response:
        """Метод для получения детальной информации о товаре."""

        product_pk = kwargs['pk']
        product = Product.objects.select_related('category').prefetch_related('images').\
        prefetch_related('tags').prefetch_related('reviews').prefetch_related('specifications').get(pk=product_pk)
        serializer = ProductDetailsSerializer(product)
        return Response(serializer.data)


class ProductReviewCreate(APIView):
    """Представление добавления отзыва о товаре. Родитель: APIView."""

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request: Request, **kwargs) -> Response:
        """Метод для добавления отзыва о товаре."""

        product_pk = kwargs['pk']
        request.data['product'] = product_pk
        serializer = ReviewSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BasketView(APIView):
    def get(self, request):
        products = request.user.profile.basket.products.all()
        serializer = ProductListSerializer(products, many=True)
        return Response(serializer.data)

    def post(self, request):
        print(request.data)
        serializer = ProductAddToBasketSerializer(data=request.data)
        if serializer.is_valid():
            print('SERIALIZER', serializer)
            print('VALIDATED DATA', serializer.validated_data)
            print(serializer.data['id'])
            print(serializer.validated_data['count'])
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
