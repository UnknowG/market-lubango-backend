from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from .models import Cart
from products.models import Product
from .serializers import CartSerializer


@api_view(["GET"])
@permission_classes([AllowAny])
def get_cart(request, cart_code):
    try:
        cart = Cart.objects.get(cart_code=cart_code)
        serializer = CartSerializer(cart)
        return Response(serializer.data)
    except Cart.DoesNotExist:
        return Response({"error": "Cart not found."}, status=status.HTTP_404_NOT_FOUND)


@api_view(["POST"])
@permission_classes([AllowAny])
def create_cart(request):
    import random
    import string
    cart_code = "".join(random.choices(string.ascii_letters + string.digits, k=11))
    cart = Cart.objects.create(cart_code=cart_code)
    serializer = CartSerializer(cart)
    return Response(serializer.data, status=status.HTTP_201_CREATED)

@api_view(["POST"])
def add_to_cart(request, cart_code):
    cart_code = request.data.get("cart_code")
    product_id = request.data.get("product_id")
    quantity = request.data.get("quantity", 1)

    cart, created = Cart.objects.get_or_create(cart_code=cart_code)

    try:
        product = Product.objects.get(id=product_id, in_stock=True)
    except Product.DoesNotExist:
        return Response(
            {"error": "Produto não encontrado ou fora de estoque."},
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Verificar se tem producto suficiente em estoque
    if product.stock_quantity < quantity:
        return Response(
            {"error": f"Quantidade solicitada excede o estoque disponível. Apenas {product.stock_quantity} disponível."},
            status=status.HTTP_400_BAD_REQUEST
        )
