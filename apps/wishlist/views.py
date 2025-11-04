from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Wishlist
from .serializers import WishlistSerializer



@api_view(["POST"])
@permission_classes([IsAuthenticated])
def add_to_wishlist(request):
    """
    Adiciona ou remove um produto da lista de desejos
    """

    product_id = request.data.get("product_id")

    if not product_id:
        return Response(
            {"error": "Produto não encontrado."},
            status=status.HTTP_404_NOT_FOUND
        )
    
    try:
        from apps.products.models import Product
        product = Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        return Response(
            {"error": "Produto não encontrado."},
            status=status.HTTP_404_NOT_FOUND
        )
    
    user = request.user

    # Verificar se o produto já está na lista de desejos
    wishlist_item, created = Wishlist.objects.get_or_create(user=user, product=product)

    if not created:
        # Se já existe, remover da lista
        wishlist_item.delete()
        return Response(
            {"message": "O Produto foi removido da lista de desejos."},
            status=status.HTTP_204_NO_CONTENT
        )
    
    # Se não existe, adicionar à lista
    serializer = WishlistSerializer(wishlist_item)
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_user_wishlist(request):
    """
    Obtém a lista de dessjos do usuário
    """
    wishlist_items = Wishlist.objects.filter(user=request.user)
    serializer = WishlistSerializer(wishlist_items, many=True)
    return Response(serializer.data)
