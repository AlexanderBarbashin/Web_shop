from django.db import transaction

from rest_framework import status

from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiExample

from shop_app.utils import get_basket, product_add_to_bakset, product_delete_from_bakset, order_users_params_get, \
    confirm_order
from shop_app.models import (
    Product,
    ProductsInBasketCount,
    Order
)
from shop_app.serializers import (
    ProductInBasketListSerializer,
    OrderDetailSerializer,
    OrderUpdateSerializer,
    ProductUpdateBasketSerializer,
    PaymentSerializer,
    OrderCreateSerializer
)

from shop_app.tasks import payment


@extend_schema(tags=['basket'])
class BasketView(APIView):
    """Представление корзины с товарами. Родитель: APIView."""

    @extend_schema(
        responses={
            200: ProductInBasketListSerializer
        }
    )
    def get(self, request: Request) -> Response:
        """Метод для отображения списка товаров в корзине."""

        basket = get_basket(request)
        products = Product.objects.prefetch_related('basket').prefetch_related('products_in_basket_count').filter(
            basket=basket,
            products_in_basket_count__count_in_basket__gt=0
        ).select_related('category').prefetch_related('images').prefetch_related('tags').prefetch_related('reviews')
        serializer = ProductInBasketListSerializer(products, context={'basket': basket.id}, many=True)
        return Response(serializer.data)

    @extend_schema(
        request=ProductUpdateBasketSerializer,
        responses={
            200: ProductInBasketListSerializer,
            400: OpenApiResponse(description='Не удалось добавить товар в корзину')
        }
    )
    def post(self, request: Request) -> Response:
        """Метод для добавления товара в корзину."""

        serializer = ProductUpdateBasketSerializer(data=request.data)
        if serializer.is_valid():
            products_serializer = product_add_to_bakset(request, serializer)
            return Response(products_serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        request=ProductUpdateBasketSerializer,
        responses={
            200: ProductInBasketListSerializer,
            400: OpenApiResponse(description='Не удалось добавить товар в корзину')
        }
    )
    def delete(self, request: Request) -> Response:
        """Метод для удаления товара из корзины."""

        serializer = ProductUpdateBasketSerializer(data=request.data)
        if serializer.is_valid():
            products_serializer = product_delete_from_bakset(request, serializer)
            return Response(products_serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(tags=['order'])
class OrderListView(APIView):
    """Представление списка заказов. Родитель: APIView."""

    @extend_schema(
        responses={
            200: OrderDetailSerializer
        }
    )
    def get(self, request: Request) -> Response:
        """Метод для отображения списка заказов."""

        profile = request.user.profile
        orders = Order.objects.select_related('profile').filter(
            profile=profile
        ).prefetch_related('products')
        orders_pk = [order.pk for order in orders]
        serializer = OrderDetailSerializer(orders, many=True, context={'orders': orders_pk})
        return Response(serializer.data)

    @extend_schema(
        request=OrderCreateSerializer,
        responses={
            200: OpenApiResponse(response=200, description='Заказ успешно создан', examples=[
                OpenApiExample(name='',value={
                    'orderId': 1
                },
                               status_codes=[200]
                               )],),
            400: OpenApiResponse(description='Заказ не создан')
        },
    )
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


@extend_schema(tags=['order'])
class OrderDetailView(APIView):
    """Представление детальной страницы заказа. Родитель: APIView."""

    @extend_schema(
        responses={
            200: OrderDetailSerializer
        }
    )
    def get(self, request: Request, **kwargs) -> Response:
        """Метод для отображения детальной страницы заказа."""

        order_pk = kwargs['pk']
        order = Order.objects.prefetch_related('products').select_related('profile').get(pk=order_pk)
        order_users_params_get(request, order)
        serializer = OrderDetailSerializer(order, context={'orders': [order_pk]})
        return Response(serializer.data)

    @extend_schema(
        request=OrderUpdateSerializer,
        responses={
            200: OpenApiResponse(description='Заказ успешно подтвержден'),
            400: OpenApiResponse(description='Заказ не подтвержден'),
        }
    )
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
            order = confirm_order(serializer, order)
            return Response({'orderId': order.id}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(tags=['payment'])
class PaymentView(APIView):
    """Представление страницы оплаты заказа. Родитель: APIView."""

    @extend_schema(
        request=PaymentSerializer,
        responses={
            200: OpenApiResponse(description='Заказ успешно оплачен'),
            400: OpenApiResponse(description='Заказ не оплачен'),
        }
    )
    def post(self, request: Request, **kwargs) -> Response:
        """Метод для оплаты заказа."""

        serializer = PaymentSerializer(data=request.data)
        if serializer.is_valid():
            order_pk = kwargs['pk']
            card_num = serializer.validated_data['number']
            updated_orders_status = payment.delay(order_pk, card_num)
            if updated_orders_status.get() == 'paid':
                return Response(status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
