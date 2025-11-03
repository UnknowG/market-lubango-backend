from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from apps.orders.models import OrderItem
from .models import Review
from .serializers import ReviewSerializer

User = get_user_model


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def add_reviews(request):
    """
    Adicinar uma avaliação para um produto
    """

    product_id = request.data.get("product_id")
    rating = request.data.get("rating")
    comment = request.data.get("comment")

    if not product_id or not rating:
        return Response(
            {"error": "É necessário o ID do produto e o rating"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        from apps.products.models import Product
        product = Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        return Response(
            {"error":"Produto não encontrado."},
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Verificar se o usuário já avaliou este produto
    if Review.objects.filter(product=product, user=request.user).exists():
        return Response(
            {"error": "Você já avaliou este produto."},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Verificar se o usuário comprou este producto
    has_purchased = OrderItem.objects.filter(
        product=product,
        order__user=request.user,
        order__status_in=["confirmed", "processing", "shipped", "delivered"]
    ).exists()

    if not has_purchased:
        return Response(
            {"error": "Podes apenas avaliar o produto você já comprou."}, status=status.HTTP_400_BAD_REQUEST
        )
    
    # Criar avaliação
    review = Review.objects.create(
        product=product,
        user=request.user,
        rating=rating,
        comment=comment
    )

    serializer = ReviewSerializer(review)
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def update_review(request, pk):
    """
    Atualiza uma avaliação existente
    """

    try: 
        review = Review.objects.get(pk=pk, user=request.user)
    except Review.DoesNotExist:
        return Response(
            {"error": "Avalaição não encontrada."},
            status=status.HTTP_404_NOT_FOUND
        )
    
    rating = request.data.get("rating")
    comment = request.data.get("comment")

    if rating:
        review.rating = rating
    if comment:
        review.comment = comment

    review.save()

    serializer = ReviewSerializer(review)
    return Response(serializer.data)
