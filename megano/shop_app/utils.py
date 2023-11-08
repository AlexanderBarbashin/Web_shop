import uuid

from catalog_app.models import Product
from django.db import transaction
from django.db.models import F, Sum
from rest_framework.request import Request
from shop_app.models import (Basket, DeliveryPrice, ExpressDeliveryPrice,
                             Order, ProductsInBasketCount)
from shop_app.serializers import (OrderUpdateSerializer,
                                  ProductInBasketListSerializer,
                                  ProductUpdateBasketSerializer)


def get_basket(request: Request) -> Basket:
    """Функция для получения корзины с товарами."""

    if request.user.is_authenticated:
        basket, _ = Basket.objects.get_or_create(user=request.user)
    else:
        try:
            basket = Basket.objects.get(session_id=request.session['anonym'])
        except:
            request.session['anonym'] = str(uuid.uuid4())
            basket = Basket.objects.create(session_id=request.session['anonym'])
    return basket

def product_add_to_bakset(request: Request, serializer: ProductUpdateBasketSerializer) -> ProductInBasketListSerializer:
    """Функция для добавления товара в корзину."""

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
        products = Product.objects.prefetch_related('basket').prefetch_related('products_in_basket_count'). \
            filter(
            basket=basket,
            products_in_basket_count__count_in_basket__gt=0
        ).select_related('category').prefetch_related('images').prefetch_related('tags').prefetch_related(
            'reviews')
        products_serializer = ProductInBasketListSerializer(products, context={'basket': basket.id}, many=True)
    return products_serializer

def product_delete_from_bakset(request: Request, serializer: ProductUpdateBasketSerializer) -> \
        ProductInBasketListSerializer:
    """Функция для удаления товара из корзины."""

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
        products = Product.objects.prefetch_related('basket').prefetch_related('products_in_basket_count'). \
            filter(
            basket=basket,
            products_in_basket_count__count_in_basket__gt=0
        ).select_related('category').prefetch_related('images').prefetch_related('tags').prefetch_related(
            'reviews')
        products_serializer = ProductInBasketListSerializer(products, context={'basket': basket.id}, many=True)
    return products_serializer

def order_users_params_get(request: Request, order: Order) -> None:
    """Функция для привязки профиля пользователя к заказу и внесения в заказ параметров пользователя."""

    if request.user.is_authenticated:
        profile = request.user.profile
        order.profile = profile
        order.fullName = profile.fullName if profile.fullName else None
        order.phone = profile.phone if profile.phone else None
        order.email = profile.email if profile.email else None
        order.save(update_fields=['profile'])

def confirm_order(serializer: OrderUpdateSerializer, order: Order) -> Order:
    """Функция для подтверждения заказа."""

    serializer.save()
    order.status = 'confirmed'
    total_cost = order.products.annotate(
        product_cost=F('price') * F('products_in_order_count__count_in_order')).aggregate(
        total_cost=Sum('product_cost'))
    delivery_price = DeliveryPrice.objects.first()
    if total_cost['total_cost'] < delivery_price.free_delivery_point:
        total_cost['total_cost'] += delivery_price.price
    if order.deliveryType == 'express':
        express_delivery_price = ExpressDeliveryPrice.objects.first().price
        total_cost['total_cost'] += express_delivery_price
    order.totalCost = total_cost['total_cost']
    order.save(update_fields=['status', 'totalCost'])
    return order