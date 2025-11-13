from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from .models import Cart, CartItem
from apps.products.models import Product
from .serializers import CartItemSerializer, CartSerializer


@api_view(["GET"])
@permission_classes([AllowAny])
def get_cart(request, cart_code):
    """
    Endpoint para obter detalhes de um carrinho pelo código.

    Parâmetros:
    - cart_code: Código do carrinho

    Retorna:
    - Detalhes do carrinho ou mensagem de erro
    """
    try:
        cart = Cart.objects.get(cart_code=cart_code)
        serializer = CartSerializer(cart)
        return Response(serializer.data)
    except Cart.DoesNotExist:
        return Response(
            {"error": "Carrinho não encontrado."}, status=status.HTTP_404_NOT_FOUND
        )


@api_view(["POST"])
@permission_classes([AllowAny])
def create_cart(request):
    """
    Endpoint para criar um novo carrinho.
    Gera um código único para o carrinho.

    Retorna:
    - Detalhes do carrinho criado
    """
    import random
    import string

    cart_code = "".join(random.choices(string.ascii_letters + string.digits, k=11))
    cart = Cart.objects.create(cart_code=cart_code)
    serializer = CartSerializer(cart)
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(["POST"])
@permission_classes([AllowAny])
def add_to_cart(request):
    """
    Endpoint para adicionar um produto ao carrinho.

    Parâmetros:
    - cart_code: Código do carrinho (no corpo da requisição)
    - product_id: ID do produto
    - quantity: Quantidade (opcional, padrão: 1)

    Retorna:
    - Detalhes do carrinho atualizado ou mensagem de erro
    """
    cart_code = request.data.get("cart_code")
    product_id = request.data.get("product_id")
    quantity = request.data.get("quantity", 1)

    if not cart_code:
        return Response(
            {"error": "Código do carrinho é obrigatório."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    cart, created = Cart.objects.get_or_create(cart_code=cart_code)

    try:
        product = Product.objects.get(id=product_id, in_stock=True)
    except Product.DoesNotExist:
        return Response(
            {"error": "Produto não encontrado ou fora de estoque."},
            status=status.HTTP_404_NOT_FOUND,
        )

    # Verificar se tem produto suficiente em estoque
    if product.stock_quantity < quantity:
        return Response(
            {
                "error": f"Quantidade solicitada excede o estoque disponível. Apenas {product.stock_quantity} disponível."
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    cartitem, created = CartItem.objects.get_or_create(product=product, cart=cart)

    if created:
        cartitem.quantity = quantity
    else:
        # Verificar se a nova quantidade em estoque é excedido
        new_quantity = cartitem.quantity + quantity
        if product.stock_quantity < new_quantity:
            return Response(
                {
                    "error": f"Quantidade solicitada excede o estoque disponível. Apenas {product.stock_quantity} disponível."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        cartitem.quantity = new_quantity

    cartitem.save()

    serializer = CartSerializer(cart)
    return Response(serializer.data)


@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def update_cartitem_quantity(request):
    """
    Endpoint para atualizar a quantidade de um item no carrinho.

    Parâmetros:
    - item_id: ID do item no carrinho
    - quantity: Nova quantidade

    Retorna:
    - Detalhes do item atualizado ou mensagem de erro
    """
    cartitem_id = request.data.get("item_id")
    quantity = request.data.get("quantity")

    try:
        cartitem = CartItem.objects.get(id=cartitem_id)
        product = cartitem.product

        # Verificar se a nova quantidade excede o estoque
        if product.stock_quantity < quantity:
            return Response(
                {
                    "error": f"Quantidade solicitada excede o estoque disponível. Apenas {product.stock_quantity} disponível."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        cartitem.quantity = quantity
        cartitem.save()

        serializer = CartItemSerializer(cartitem)
        return Response(
            {
                "data": serializer.data,
                "message": "Item no carrinho atualizado com sucesso!",
            }
        )
    except CartItem.DoesNotExist:
        return Response(
            {"error": "Item não encontrado no carrinho."},
            status=status.HTTP_404_NOT_FOUND,
        )


@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def delete_cartitem(request, pk):
    """
    Endpoint para remover um item do carrinho.

    Parâmetros:
    - pk: ID do item no carrinho

    Retorna:
    - Mensagem de sucesso ou erro
    """
    try:
        cartitem = CartItem.objects.get(id=pk)
        cartitem.delete()
        return Response(
            "Item do carrinho deletado com sucesso.", status=status.HTTP_204_NO_CONTENT
        )
    except CartItem.DoesNotExist:
        return Response(
            {"error": "Item não encontrado no carrinho."},
            status=status.HTTP_404_NOT_FOUND,
        )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_user_cart(request):
    """
    Endpoint para criar ou obter o carrinho do usuário autenticado.

    Retorna:
    - Detalhes do carrinho do usuário
    """
    cart, created = Cart.objects.get_or_create(user=request.user)
    if created:
        # Gerar um código para o carrinho
        import random
        import string

        cart_code = "".join(random.choices(string.ascii_letters + string.digits, k=11))
        cart.cart_code = cart_code
        cart.save()
    serializer = CartSerializer(cart)
    return Response(serializer.data)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_user_cart(request):
    """
    Endpoint para obter o carrinho do usuário autenticado.

    Retorna:
    - Detalhes do carrinho do usuário ou mensagem de erro
    """
    try:
        cart = Cart.objects.get(user=request.user)
        serializer = CartSerializer(cart)
        return Response(serializer.data)
    except Cart.DoesNotExist:
        return Response(
            {"error": "Carrinho não encontrado."}, status=status.HTTP_404_NOT_FOUND
        )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def merge_carts(request):
    """
    Endpoint para mesclar o carrinho temporário com o carrinho do usuário.

    Parâmetros:
    - temp_cart_code: Código do carrinho temporário

    Retorna:
    - Detalhes do carrinho mesclado ou mensagem de erro
    """
    try:
        user_cart, created = Cart.objects.get_or_create(user=request.user)
        if created:
            import random
            import string

            user_cart.cart_code = "".join(
                random.choices(string.ascii_letters + string.digits, k=11)
            )
            user_cart.save()

        temp_cart_code = request.data.get("temp_cart_code")
        if temp_cart_code:
            try:
                temp_cart = Cart.objects.get(cart_code=temp_cart_code)
                for item in temp_cart.cartitems.all():
                    if (
                        not item.product.in_stock
                        or item.product.stock_quantity < item.quantity
                    ):
                        continue  # Pular itens fora de estoque

                    CartItem.objects.update_or_create(
                        cart=user_cart,
                        product=item.product,
                        defaults={"quantity": item.quantity},
                    )
                temp_cart.delete()
            except Cart.DoesNotExist:
                pass

        serializer = CartSerializer(user_cart)
        return Response(serializer.data)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
