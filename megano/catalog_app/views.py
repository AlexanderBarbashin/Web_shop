from datetime import datetime

from catalog_app.models import Category, Product, Review, Tag
from catalog_app.serializers import (
    BannerProductListSerializer,
    CategorySerializer,
    ProductDetailsSerializer,
    ProductListSerializer,
    ProductSaleSerializer,
    ReviewSerializer,
    TagSerializer,
)
from catalog_app.utils import (
    ProductListFilter,
    ProductListViewPagination,
    SaleListViewPagination,
    request_handler,
)
from django.db.models import Count, Q, QuerySet, Sum
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import OpenApiExample, OpenApiResponse, extend_schema
from rest_framework import permissions, status
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.generics import CreateAPIView, ListAPIView, RetrieveAPIView
from rest_framework.request import Request
from rest_framework.response import Response


@extend_schema(
    tags=["catalog"],
    responses={
        200: OpenApiResponse(
            response=200,
            description="successful operation",
            examples=[
                OpenApiExample(
                    name="",
                    value={
                        "id": 123,
                        "title": "video card",
                        "image": {"src": "/3.png", "alt": "Image alt string"},
                        "subcategories": [
                            {
                                "id": 123,
                                "title": "video card",
                                "image": {"src": "/3.png", "alt": "Image alt string"},
                            }
                        ],
                    },
                    status_codes=[200],
                )
            ],
        ),
    },
)
class CategoryView(ListAPIView):
    """Представление категорий и подкатегорий товаров. Родитель: ListAPIView."""

    # Получаем главные категории, содержащие хотя бы один продукт или подкатегорию
    main_categories = (
        Category.objects.filter(main_category=None)
        .prefetch_related("subcategories")
        .prefetch_related("products")
        .annotate(prods_count=Count("products"))
        .annotate(subcats_count=Count("subcategories"))
        .filter(Q(prods_count__gt=0) | Q(subcats_count__gt=0))
    )

    # Исключаем главные категории, которые не содержат ни одного продукта и ни одной активной подкатегории
    # (подкатегории, содержащей хотя бы один продукт)
    for category in main_categories:
        subcategories_products_sum = (
            category.subcategories.all()
            .prefetch_related("products")
            .annotate(subcats_prods_count=Count("products"))
            .aggregate(subcats_prods_sum=Sum("subcats_prods_count"))
        )
        if (
            category.prods_count == 0
            and subcategories_products_sum["subcats_prods_sum"] == 0
        ):
            main_categories = main_categories.exclude(id=category.id)

    queryset = main_categories
    serializer_class = CategorySerializer


@extend_schema(tags=["tags"])
class TagsView(ListAPIView):
    """Представление тэгов товаров. Родитель: ListAPIView."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer


@extend_schema(tags=["catalog"])
class ProductListView(ListAPIView):
    """Представление списка товаров. Родитель: ListAPIView."""

    queryset = (
        Product.objects.all()
        .select_related("category")
        .prefetch_related("images")
        .prefetch_related("tags")
        .prefetch_related("reviews")
        .annotate(product_reviews=Count("reviews"))
    )
    serializer_class = ProductListSerializer
    pagination_class = ProductListViewPagination
    filter_backends = [SearchFilter, DjangoFilterBackend, OrderingFilter]
    filterset_class = ProductListFilter
    ordering_fields = ["rating", "price", "product_reviews", "date"]
    search_fields = ["title"]

    def get(self, request: Request, *args) -> Response:
        """Метод для получения списка товаров."""

        _mutable = request.query_params._mutable
        request.query_params._mutable = True
        request = request_handler(request)
        request.query_params._mutable = _mutable
        return super().get(request, *args)


@extend_schema(tags=["catalog"])
class ProductPopularListView(ListAPIView):
    """Представление списка топ-товаров. Родитель: ListAPIView."""

    queryset = (
        Product.objects.filter(count__gt=0)
        .select_related("category")
        .prefetch_related("images")
        .prefetch_related("tags")
        .prefetch_related("reviews")
        .prefetch_related("products_in_order_count")
        .annotate(
            purchase_count=Sum(
                "products_in_order_count__count_in_order",
                filter=Q(products_in_order_count__order__status="paid"),
            )
        )
        .order_by("-rating", "-purchase_count")[:5]
    )
    serializer_class = ProductListSerializer


@extend_schema(tags=["catalog"])
class ProductLimitedListView(ListAPIView):
    """Представление списка товаров из серии 'ограниченный тираж'. Родитель: ListAPIView."""

    queryset = (
        Product.objects.filter(count__gt=0)
        .filter(limited=True)
        .select_related("category")
        .prefetch_related("images")
        .prefetch_related("tags")
        .prefetch_related("reviews")
        .order_by("-rating")[:5]
    )
    serializer_class = ProductListSerializer


@extend_schema(tags=["catalog"])
class ProductSaleListView(ListAPIView):
    """Представление списка товаров со скидками. Родитель: ListAPIView."""

    today = datetime.now().date()
    queryset = (
        Product.objects.filter(count__gt=0)
        .select_related("sale")
        .filter(sale__dateFrom__lte=today)
        .filter(sale__dateTo__gte=today)
        .prefetch_related("images")
        .order_by("sale__salePrice")
    )
    serializer_class = ProductSaleSerializer
    pagination_class = SaleListViewPagination


@extend_schema(tags=["catalog"])
class BannerListView(ListAPIView):
    """Представление банеров с товарами из избранных категорий. Родитель: ListAPIView."""

    serializer_class = BannerProductListSerializer

    def get_queryset(self) -> QuerySet:
        """Метод для получения QuerySet из самых дешевых товаров в избранных категориях."""

        categories = (
            Category.objects.prefetch_related("products")
            .filter(products__count__gt=0)
            .order_by("?")[:5]
        )
        products_in_banners_list = [
            Product.objects.select_related("category")
            .filter(category=category, count__gt=0)
            .order_by("price")[:1][0]
            .id
            for category in categories
        ]
        queryset = (
            Product.objects.filter(id__in=products_in_banners_list)
            .select_related("category")
            .prefetch_related("images")
            .prefetch_related("tags")
            .prefetch_related("reviews")
        )
        return queryset


@extend_schema(tags=["product"])
class ProductDetailView(RetrieveAPIView):
    """Представление детальной страницы товара. Родитель: RetrieveAPIView."""

    queryset = (
        Product.objects.select_related("category")
        .prefetch_related("images")
        .prefetch_related("tags")
        .prefetch_related("reviews")
        .prefetch_related("specifications")
    )
    serializer_class = ProductDetailsSerializer


@extend_schema(tags=["product"])
class ProductReviewCreate(CreateAPIView):
    """Представление добавления отзыва о товаре. Родитель: CreateAPIView."""

    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request: Request, *args, **kwargs) -> Response:
        """Метод для создания отзыва от товаре."""

        product_pk = kwargs["pk"]
        request.data["product"] = product_pk
        super().create(request, *args, **kwargs)
        reviews = Review.objects.select_related("product").filter(product=product_pk)
        reviews_serializer = ReviewSerializer(reviews, many=True)
        return Response(reviews_serializer.data, status=status.HTTP_200_OK)
