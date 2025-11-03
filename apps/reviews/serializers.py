from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import ProductRating, Review

User = get_user_model()

class ReviewSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Review
        fields = ["id", "user", "rating", "comment", "created_at", "updated_at"]


class ProductRatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductRating
        fields = ["average_rating", "total_reviews"]
