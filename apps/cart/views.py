from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from .models import Cart, CartItem
from products.models import Product
from .serializers import CartItemSerializer, CartSerializer


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
    
    cartitem, created = CartItem.objects.get_or_create(product=product, cart=cart)

    if created:
        cartitem.quantity = quantity
    else:
        # Verificar se a nova quantidade in estoque é excedido
        new_quantity = cartitem.quantity + quantity
        if product.stock_quantity < new_quantity:
            return Response(
                {"error": f"Quantidade solicitada excede o estoque disponível. Apenas {product.stock_quantity} disponível."},
                status=status.HTTP_400_BAD_REQUEST
            )
        cartitem.quantity = new_quantity
    
    cartitem.save()

    serializer = CartSerializer(cart)
    return Response(serializer.data)


@api_view(["PUT"])
def update_cartitem_quantity(request):
    cartitem_id = request.data.get("item_id")
    quantity = request.data.get("quantity")

    try:
        cartitem = CartItem.objects.get(id=cartitem_id)
        product = cartitem.product

        # Verificar se a nova quantidade excede o estoque
        if product.stock_quantity < quantity:
            return Response(
                {"error": f"Quantidade solicitada excede o estoque disponível. Apenas {product.stock_quantity} disponível."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        cartitem.quantity = quantity
        cartitem.save()

        serializer = CartItemSerializer(cartitem)
        return Response(
            {"data": serializer.data, "message": "Item no carrinho atualizado com sucesso!"}
        )
    except CartItem.DoesNotExist:
        return Response(
            {"error": "Item não encontrado no carrinho."},
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(["DELETE"])
def delete_cartitem(request, pk):
    try:
        cartitem = CartItem.objects.get(id=pk)
        cartitem.delete()
        return Response("Item do carrinho deletado com sucesso.", status=status.HTTP_204_NO_CONTENT)
    except CartItem.DoesNotExist:
        return Response(
            {"error": "Item não encontrado no carrinho."},
            status=status.HTTP_404_NOT_FOUND
        )
