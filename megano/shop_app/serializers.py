from datetime import datetime
import time
from typing import List, Dict

from rest_framework import serializers

from catalog_app.serializers import ProductListSerializer
from shop_app.models import Product, Order


class ProductInBasketListSerializer(ProductListSerializer):
    """Сериалайзер для отображения списка товаров в корзине. Родитель: ProductListSerializer."""

    count = serializers.SerializerMethodField()

    def get_count(self, obj: Product) -> int:
        """Метод для получения количества товара в корзине."""

        products_in_basket_count = obj.products_in_basket_count.get(basket=self.context['basket'])
        return products_in_basket_count.count_in_basket


class ProductUpdateBasketSerializer(serializers.ModelSerializer):
    """Сериалайзер для добавления/удаления товара в корзину/из корзины. Родитель: ModelSerializer."""

    id = serializers.IntegerField()

    class Meta:
        model = Product
        fields = ['id', 'count']


class ProductInOrderListSerializer(ProductListSerializer):
    """Сериалайзер для отображения списка товаров в заказе. Родитель: ProductListSerializer."""
    count = serializers.SerializerMethodField()

    def get_count(self, obj: Product) -> int:
        """Метод для получения количества товара в заказе."""

        products_in_order_count = obj.products_in_order_count.filter(order__in=self.context['orders']).first()
        return products_in_order_count.count_in_order


class OrderCreateSerializer(serializers.ModelSerializer):
    """Сериалайзер для создания заказа. Родитель: ModelSerializer."""

    products = ProductListSerializer(many=True)

    class Meta:
        model = Order
        fields = ['products']

    def create(self, validated_data: List[Dict]) -> Order:
        """Метод для создания заказа."""

        products = validated_data.pop('products')
        order = Order.objects.create()
        for product in products:
            order.products.add(product['id'], through_defaults={'count_in_order': product['count']})
        return order


class OrderDetailSerializer(serializers.ModelSerializer):
    """Сериалайзер для отображения детальной страницы заказа. Родитель: ModelSerializer."""

    products = ProductInOrderListSerializer(many=True)

    class Meta:
        model = Order
        fields = ['id', 'createdAt', 'fullName', 'email', 'phone', 'deliveryType', 'paymentType', 'totalCost', 'status',
                  'city', 'address', 'products']


class OrderUpdateSerializer(serializers.ModelSerializer):
    """Сериалайзер для подтверждения заказа. Родитель: ModelSerializer."""

    totalCost = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = ['fullName', 'email', 'phone', 'deliveryType', 'paymentType', 'totalCost', 'city', 'address']


class PaymentSerializer(serializers.Serializer):
    """Сериалайзер для оплаты заказа. Родитель: Serializer."""

    number = serializers.CharField(min_length=16)
    month = serializers.IntegerField(min_value=1, max_value=12)
    year = serializers.IntegerField(min_value=23, max_value=99)
    code = serializers.CharField(min_length=3, max_length=3)
    name = serializers.CharField(max_length=150)

    def validate_number(self, value: str) -> str:
        """Метод для валидации номера карты."""

        if value.isdigit():
            return value
        raise serializers.ValidationError('Номер карты не соответствует формату!')

    def validate_code(self, value: str) -> str:
        """Метод для валидации CVV кода карты."""

        if value.isdigit():
            return value
        raise serializers.ValidationError('Код CVV не соответствует формату!')

    def validate_name(self, value: str) -> str:
        """Метод для валидации ФИО владельца карты."""

        new_value = value.replace(' ', '').replace("'", '')
        if new_value.isalpha():
            return value
        raise serializers.ValidationError('ФИО не соответствует формату!')

    def validate(self, data: Dict) -> Dict:
        """Метод для валидации срока действия карты."""

        card_date_string = '{year}-{month}'.format(
            year=str(data['year']),
            month=str(data['month'])
        )
        card_date = time.strptime(card_date_string, '%y-%m')
        now = datetime.now()
        today_string = '{year}-{month}'.format(
            year=str(now.year)[2:],
            month=str(now.month)
        )
        today = time.strptime(today_string, '%y-%m')
        if today > card_date:
            raise serializers.ValidationError('Карта просрочена!')
        return data
