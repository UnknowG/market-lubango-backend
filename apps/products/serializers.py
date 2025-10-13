from rest_framework import serializers
from .models import Category, Product


class ProductListSerializer(serializers.ModelSerializer):
    store_name = serializers.CharField(source="store.name", read_only=True)

    class Meta:
        model = Product
        fields = ["id", "name", "slug", "image", "price", "store_name", "in_stock"]


class ProductDetailSerializer(serializers.ModelSerializer):
    store = serializers.StringRelatedField(read_only=True)
    category = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Product
        fields = ["id", "name", "slug", "description", "image", "price", "store", "category", "in_stock", "stock_quantity", "created_at"]


class CategoryListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name", "image", "slug"]


class CategoryDetailSerializer(serializers.ModelSerializer):
    products = ProductListSerializer(many=True, read_only=True)

    class Meta:
        model = Category
        fields = ["id", "name", "image", "products"]
