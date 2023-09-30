from django.urls import path

from shop_app.views import (
    CategoryView,
    ProductDetailView,
    TagsView,
    ProductReviewCreate,
    ProductListView,
    ProductPopularListView,
    ProductLimitedListView,
    ProductSaleListView,
    BannerListView,
    BasketView,
    OrderListView,
    OrderDetailView,
    PaymentView
)

urlpatterns = [
    path('categories/', CategoryView.as_view(), name='categories'),
    path('catalog/', ProductListView.as_view(), name='catalog'),
    path('products/popular/', ProductPopularListView.as_view(), name='products_popular'),
    path('products/limited/', ProductLimitedListView.as_view(), name='products_limited'),
    path('sale/', ProductSaleListView.as_view(), name='products_sales'),
    path('banners/', BannerListView.as_view(), name='banners'),
    path('basket/', BasketView.as_view(), name='basket'),
    path('orders/', OrderListView.as_view(), name='orders'),
    path('order/<int:pk>/', OrderDetailView.as_view(), name='order_detail'),
    path('payment/<int:pk>/', PaymentView.as_view(), name='payment'),
    path('product/<int:pk>/', ProductDetailView.as_view(), name='product'),
    path('product/<int:pk>/reviews/', ProductReviewCreate.as_view(), name='review_create'),
    path('tags/', TagsView.as_view(), name='tags'),
]