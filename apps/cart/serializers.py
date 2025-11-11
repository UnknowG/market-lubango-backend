from rest_framework import serializers
from .models import Cart, CartItem
from apps.products.serializers import ProductListSerializer


class CartItemSerializer(serializers.ModelSerializer):
    """
    Serializer para itens do carrinho de compras.
    Inclui informações do produto e calcula o subtotal.
    """

    product = ProductListSerializer(read_only=True, help_text="Produto no carrinho")
    sub_total = serializers.SerializerMethodField(
        help_text="Subtotal do item (preço * quantidade)"
    )

    class Meta:
        model = CartItem
        fields = ["id", "product", "quantity", "sub_total"]

    def get_sub_total(self, obj):
        """
        Calcula o subtotal do item (preço * quantidade).
        """
        total = obj.product.price * obj.quantity
        return total


class CartSerializer(serializers.ModelSerializer):
    """
    Serializer para o carrinho de compras.
    Inclui todos os itens e calcula o total do carrinho.
    """

    cartitems = CartItemSerializer(
        read_only=True, many=True, help_text="Itens do carrinho"
    )
    cart_total = serializers.SerializerMethodField(help_text="Total do carrinho")

    class Meta:
        model = Cart
        fields = ["id", "cart_code", "cartitems", "cart_total"]

    def get_cart_total(self, cart):
        """
        Calcula o total do carrinho somando os subtotais de todos os itens.
        """
        items = cart.cartitems.all()
        total = sum([item.quantity * item.product.price for item in items])
        return total


class CartStatSerializer(serializers.ModelSerializer):
    """
    Serializer para estatísticas do carrinho.
    Inclui apenas informações básicas e a quantidade total de itens.
    """

    total_quantity = serializers.SerializerMethodField(
        help_text="Quantidade total de itens no carrinho"
    )

    class Meta:
        model = Cart
        fields = ["id", "cart_code", "total_quantity"]

    def get_total_quantity(self, cart):
        """
        Calcula a quantidade total de itens no carrinho.
        """
        items = cart.cartitems.all()
        total = sum([item.quantity for item in items])
        return total
