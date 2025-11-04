from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Wishlist
from apps.products.serializers import ProductListSerializer


User = get_user_model()


class WishlistSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    product = ProductListSerializer(read_only=True)

    class Meta:
        model = Wishlist
        fields = ["id", "user", "product", "created_at"]
