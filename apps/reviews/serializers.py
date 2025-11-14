from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import ProductRating, Review

User = get_user_model()


class ReviewSerializer(serializers.ModelSerializer):
    """
    Serializer para avaliações de produtos.
    """

    user = serializers.SerializerMethodField(read_only=True)
    product_name = serializers.CharField(source='product.name', read_only=True)
    rating_display = serializers.CharField(source='get_rating_display', read_only=True)

    class Meta:
        model = Review
        fields = [
            "id", 
            "user", 
            "product_name",
            "rating", 
            "rating_display",
            "comment", 
            "created_at", 
            "updated_at"
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def get_user(self, obj):
        """
        Retorna apenas informações necessárias do usuário.
        Evita expor dados sensíveis.
        """
        return {
            "id": obj.user.id,
            "username": obj.user.username,
        }


class ProductRatingSerializer(serializers.ModelSerializer):
    """
    Serializer para classificação média de produtos.
    """

    class Meta:
        model = ProductRating
        fields = ["average_rating", "total_reviews", "updated_at"]
        read_only_fields = ["average_rating", "total_reviews", "updated_at"]
