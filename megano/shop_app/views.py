from datetime import datetime

from django.db import transaction
from django.db.models import Count, Sum, F, Q

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, permissions
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.generics import ListAPIView, RetrieveAPIView, CreateAPIView
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from shop_app.utils import ProductListFilter, ProductListViewPagination, SaleListViewPagination, get_basket
from shop_app.models import (
    Category,
    Product,
    Tag,
    ProductsInBasketCount,
    Order,
    Review,
    ExpressDeliveryPrice,
    DeliveryPrice
)
from shop_app.serializers import (
    CategorySerializer,
    TagSerializer,
    ReviewSerializer,
    ProductDetailsSerializer,
    ProductListSerializer,
    ProductSaleSerializer,
    BannerProductListSerializer,
    ProductInBasketListSerializer,
    OrderDetailSerializer,
    OrderUpdateSerializer,
    ProductUpdateBasketSerializer,
    PaymentSerializer,
    OrderCreateSerializer
)


class CategoryView(ListAPIView):
    """Представление категорий и подкатегорий товаров. Родитель: ListAPIView."""

    queryset = Category.objects.filter(main_category=None).prefetch_related('subcategories').\
        prefetch_related('products').annotate(prods_count=Count('products')).filter(prods_count__gt=0)
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

    categories = Category.objects.prefetch_related('products').filter(products__count__gt=0).order_by('?')[:5]
    products_in_banners_list = [
        Product.objects.select_related('category').filter(category=category, count__gt=0).\
            order_by('price')[:1][0].id
        for category
        in categories
    ]
    queryset = Product.objects.filter(id__in=products_in_banners_list).select_related('category').\
        prefetch_related('images').prefetch_related('tags').prefetch_related('reviews')
    serializer_class = BannerProductListSerializer


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
        return Response(reviews_serializer.data, status=status.HTTP_201_CREATED)


class BasketView(APIView):
    """Представление корзины с товарами. Родитель: APIView."""

    def get(self, request: Request) -> Response:
        """Метод для отображения списка товаров в корзине."""

        basket = get_basket(request)
        products = Product.objects.prefetch_related('basket').prefetch_related('products_in_basket_count').filter(
            basket=basket,
            products_in_basket_count__count_in_basket__gt=0
        ).select_related('category').prefetch_related('images').prefetch_related('tags').prefetch_related('reviews')
        serializer = ProductInBasketListSerializer(products, context={'basket': basket.id}, many=True)
        return Response(serializer.data)

    def post(self, request: Request) -> Response:
        """Метод для добавления товара в корзину."""

        serializer = ProductUpdateBasketSerializer(data=request.data)
        if serializer.is_valid():
            basket = get_basket(request)
            product_id = serializer.validated_data['id']
            product = Product.objects.get(id=product_id)
            count = serializer.validated_data['count']
            product_in_basket, _ = ProductsInBasketCount.objects.get_or_create(basket=basket, product=product)
            with transaction.atomic():
                product.count -= count
                product.save(update_fields=['count'])
                product_in_basket.count_in_basket += count
                product_in_basket.save(update_fields=['count_in_basket'])
                products = Product.objects.prefetch_related('basket').prefetch_related('products_in_basket_count').\
                    filter(
                    basket=basket,
                    products_in_basket_count__count_in_basket__gt=0
                ).select_related('category').prefetch_related('images').prefetch_related('tags').prefetch_related(
                    'reviews')
                products_serializer = ProductInBasketListSerializer(products, context={'basket': basket.id}, many=True)
                return Response(products_serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request: Request) -> Response:
        """Метод для удаления товара из корзины."""

        serializer = ProductUpdateBasketSerializer(data=request.data)
        if serializer.is_valid():
            basket = get_basket(request)
            product_id = serializer.validated_data['id']
            product = Product.objects.get(id=product_id)
            count = serializer.validated_data['count']
            product_in_basket = ProductsInBasketCount.objects.get(basket=basket, product=product)
            with transaction.atomic():
                product.count += count
                product.save(update_fields=['count'])
                product_in_basket.count_in_basket -= count
                product_in_basket.save(update_fields=['count_in_basket'])
                products = Product.objects.prefetch_related('basket').prefetch_related('products_in_basket_count').\
                    filter(
                    basket=basket,
                    products_in_basket_count__count_in_basket__gt=0
                ).select_related('category').prefetch_related('images').prefetch_related('tags').prefetch_related(
                    'reviews')
                products_serializer = ProductInBasketListSerializer(products, context={'basket': basket.id}, many=True)
                return Response(products_serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class OrderListView(APIView):
    """Представление списка заказов. Родитель: APIView."""

    def get(self, request: Request) -> Response:
        """Метод для отображения списка заказов."""

        profile = request.user.profile
        orders = Order.objects.select_related('profile').filter(
            profile=profile
        ).prefetch_related('products')
        orders_pk = [order.pk for order in orders]
        serializer = OrderDetailSerializer(orders, many=True, context={'orders': orders_pk})
        return Response(serializer.data)

    def post(self, request: Request) -> Response:
        """Метод для создания заказа."""

        serializer = OrderCreateSerializer(data={'products': request.data})
        if serializer.is_valid():
            with transaction.atomic():
                order = serializer.save()
                basket = get_basket(request)
                products_in_basket = ProductsInBasketCount.objects.filter(
                    basket=basket,
                    count_in_basket__gt=0
                )
                for product in products_in_basket:
                    product.count_in_basket = 0
                ProductsInBasketCount.objects.bulk_update(products_in_basket, ['count_in_basket'])
                return Response({'orderId': order.id}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class OrderDetailView(APIView):
    """Представление детальной страницы заказа. Родитель: APIView."""

    def get(self, request: Request, **kwargs) -> Response:
        """Метод для отображения детальной страницы заказа."""

        order_pk = kwargs['pk']
        order = Order.objects.prefetch_related('products').select_related('profile').get(pk=order_pk)
        if request.user.is_authenticated:
            profile = request.user.profile
            order.profile = profile
            order.fullName = profile.fullName if profile.fullName else None
            order.phone = profile.phone if profile.phone else None
            order.email = profile.email if profile.email else None
            order.save(update_fields=['profile'])
        serializer = OrderDetailSerializer(order, context={'orders': [order_pk]})
        return Response(serializer.data)

    def post(self, request: Request, **kwargs) -> Response:
        """Метод для подтверждения заказа."""

        order_pk = kwargs['pk']
        order = Order.objects.prefetch_related('products').prefetch_related('products_in_order_count').select_related(
            'profile').get(pk=order_pk)
        if order.status == 'paid':
            return Response('Заказ № {order} уже оплачен!'.format(
                order=order_pk
            ),
            status=status.HTTP_400_BAD_REQUEST)
        elif order.status == 'confirmed':
            return Response({'orderId': order.id}, status=status.HTTP_200_OK)
        serializer = OrderUpdateSerializer(order, data=request.data)
        if serializer.is_valid():
            serializer.save()
            order.status = 'confirmed'
            total_cost = order.products.annotate(
                product_cost=F('price') * F('products_in_order_count__count_in_order')).aggregate(
                total_cost=Sum('product_cost'))
            delivery_price = DeliveryPrice.objects.first()
            if total_cost['total_cost'] < delivery_price.free_delivery_point:
                total_cost['total_cost'] += delivery_price.price
            express_delivery_price = ExpressDeliveryPrice.objects.first().price
            if order.deliveryType == 'express':
                total_cost['total_cost'] += express_delivery_price
            order.totalCost = total_cost['total_cost']
            order.save(update_fields=['status', 'totalCost'])
            return Response({'orderId': order.id}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PaymentView(APIView):
    """Представление страницы оплаты заказа. Родитель: APIView."""

    def post(self, request: Request, **kwargs) -> Response:
        """Метод для оплаты заказа."""

        serializer = PaymentSerializer(data=request.data)
        if serializer.is_valid():
            order_pk = kwargs['pk']
            order = Order.objects.get(pk=order_pk)
            order.status = 'paid'
            order.save(update_fields=['status'])
            return Response(status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
