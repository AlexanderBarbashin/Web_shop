from django.urls import path

from shop_app.views import (
    BasketView,
    OrderListView,
    OrderDetailView,
    PaymentView
)

urlpatterns = [
    path('basket', BasketView.as_view(), name='basket'),
    path('orders', OrderListView.as_view(), name='orders'),
    path('order/<int:pk>', OrderDetailView.as_view(), name='order_detail'),
    path('payment/<int:pk>', PaymentView.as_view(), name='payment'),
]