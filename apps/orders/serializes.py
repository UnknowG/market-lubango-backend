from rest_framework import serializers
from .models import Order, OrderItem, Payment
from apps.products.serializers import ProductListSerializer


class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductListSerializer(read_only=True)

    class Meta:
        model = OrderItem
        fields = ["id", "product", "quantity", "price"]


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(read_only=True, many=True)

    class Meta:
        model = Order
        fields = [
            "id",
            "order_number",
            "status",
            "payment_status",
            "total_amount",
            "shipping_address",
            "created_at",
            "updated_at",
            "items",
        ]


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = [
            "id",
            "payment_method",
            "payment_status",
            "transaction_id",
            "amount",
            "reference_number",
            "created_at",
            "updated_at",
        ]


class CreateOrderSerializer(serializers.Serializer):
    cart_code = serializers.CharField()
    shipping_address = serializers.CharField()
    payment_method = serializers.ChoiceField(choices=Payment.PAYMENT_METHOD_CHOICES)
    reference_number = serializers.CharField(
        required=False, allow_blank=True, allow_null=True
    )
