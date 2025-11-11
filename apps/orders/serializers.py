from rest_framework import serializers
from .models import Order, OrderItem, Payment
from apps.products.serializers import ProductListSerializer


class OrderItemSerializer(serializers.ModelSerializer):
    """
    Serializer para itens de pedido.
    Inclui informações do produto.
    """

    product = ProductListSerializer(read_only=True, help_text="Produto do pedido")

    class Meta:
        model = OrderItem
        fields = ["id", "product", "quantity", "price"]


class OrderSerializer(serializers.ModelSerializer):
    """
    Serializer para pedidos.
    Inclui todos os itens do pedido.
    """

    items = OrderItemSerializer(read_only=True, many=True, help_text="Itens do pedido")

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
    """
    Serializer para pagamentos.
    """

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
    """
    Serializer para criação de pedidos.
    """

    cart_code = serializers.CharField(help_text="Código do carrinho de compras")
    shipping_address = serializers.CharField(help_text="Endereço de entrega")
    payment_method = serializers.ChoiceField(
        choices=Payment.PAYMENT_METHOD_CHOICES, help_text="Método de pagamento"
    )
    reference_number = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True,
        help_text="Número de referência (para pagamentos por referência)",
    )
