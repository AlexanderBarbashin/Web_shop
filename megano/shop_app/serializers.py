from django.template.defaulttags import url
from rest_framework import serializers

from shop_app.models import Image, Category, Product, Tag, Review, Specification


class ImageSerializer(serializers.ModelSerializer):
    """Сериалайзер модели изображения. Родитель: ModelSerializer."""

    src = serializers.SerializerMethodField()

    class Meta:
        model = Image
        fields = ['src', 'alt']

    def get_src(self, obj: Image) -> url:
        """Метод для получения ссылки на изображение."""
        return obj.src.url


class SubcategorySerializer(serializers.Serializer):
    """Сериалайзер модели подкатегории. Родитель: Serializer."""

    def to_representation(self, value: Category) -> dict:
        """Метод для рекурсивной сериализации подкатегорий."""

        serialaizer = self.parent.parent.__class__(value, context=self.context)
        return serialaizer.data


class CategorySerializer(serializers.ModelSerializer):
    """Сериалайзер модели категории. Родитель: ModelSerializer."""

    image = ImageSerializer(read_only=True)
    subcategories = SubcategorySerializer(many=True)

    class Meta:
        model = Category
        fields = ['id', 'title', 'image', 'subcategories']


class TagSerializer(serializers.ModelSerializer):
    """Сериалайзер модели тэга. Родитель: ModelSerializer."""

    class Meta:
        model = Tag
        fields = ['id', 'name']


class ReviewSerializer(serializers.ModelSerializer):
    """Сериалайзер модели отзыва. Родитель: ModelSerializer."""

    class Meta:
        model = Review
        fields = '__all__'


class SpecificationSerializer(serializers.ModelSerializer):
    """Сериалайзер модели характеристики. Родитель: ModelSerializer."""

    class Meta:
        model = Specification
        fields = '__all__'


class ProductListSerializer(serializers.ModelSerializer):
    """Сериалайзер модели продукта. Родитель: ModelSerializer."""

    category = CategorySerializer()
    images = ImageSerializer(many=True)
    tags = TagSerializer(many=True)
    reviews = ReviewSerializer(many=True)

    class Meta:
        model = Product
        fields = [
            'id', 'category', 'price', 'count', 'date', 'title', 'description', 'freeDelivery', 'images', 'tags',
            'reviews', 'rating'
        ]


class ProductSaleSerializer(serializers.ModelSerializer):
    """Сериалайзер модели продукта со скидкой. Родитель: ModelSerializer."""

    salePrice = serializers.CharField(source='sale.salePrice')
    dateFrom = serializers.DateField(source='sale.dateFrom')
    dateTo = serializers.DateField(source='sale.dateTo')
    images = ImageSerializer(many=True)

    class Meta:
        model = Product
        fields = ['id', 'price', 'salePrice', 'dateFrom', 'dateTo', 'title', 'images']


class BannerProductListSerializer(ProductListSerializer):
    """Сериалайзер модели продукта для баннера. Родитель: ProductListSerializer."""

    category = serializers.SerializerMethodField()

    def get_category(self, obj: Product) -> int:
        """Метод для получения id категории."""

        return obj.category.id

class ProductDetailsSerializer(serializers.ModelSerializer):
    """Сериалайзер для отображения детальной страницы продука. Родитель: ModelSerializer."""

    category = CategorySerializer()
    images = ImageSerializer(many=True)
    tags = TagSerializer(many=True)
    reviews = ReviewSerializer(many=True)
    specifications = SpecificationSerializer(many=True)

    class Meta:
        model = Product
        fields = [
            'id', 'category', 'price', 'count', 'date', 'title', 'description', 'fullDescription', 'freeDelivery',
            'images', 'tags', 'reviews', 'specifications', 'rating'
        ]


class ProductAddToBasketSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()

    class Meta:
        model = Product
        fields = ['id', 'count']

