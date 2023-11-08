from django.urls import path

from catalog_app.views import (
    CategoryView,
    ProductDetailView,
    TagsView,
    ProductReviewCreate,
    ProductListView,
    ProductPopularListView,
    ProductLimitedListView,
    ProductSaleListView,
    BannerListView,
)

urlpatterns = [
    path('categories', CategoryView.as_view(), name='categories'),
    path('catalog', ProductListView.as_view(), name='catalog'),
    path('products/popular', ProductPopularListView.as_view(), name='products_popular'),
    path('products/limited', ProductLimitedListView.as_view(), name='products_limited'),
    path('sale', ProductSaleListView.as_view(), name='products_sales'),
    path('banners', BannerListView.as_view(), name='product_banners'),
    path('product/<int:pk>', ProductDetailView.as_view(), name='product'),
    path('product/<int:pk>/reviews', ProductReviewCreate.as_view(), name='review_create'),
    path('tags', TagsView.as_view(), name='tags'),
]
