from rest_framework import serializers
from .models import OrderItem
from apps.products.serializers import ProductListSerializer



class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductListSerializer(read_only=True)

    class Meta:
        model = OrderItem
        fields = ["id", "product", "quantity", "price"]
