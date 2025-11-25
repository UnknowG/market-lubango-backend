from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.db.models import Q
from .models import Category, Product
from apps.accounts.models import Store
from .serializers import (
    CategoryDetailSerializer,
    CategoryListSerializer,
    ProductCreateSerializer,
    ProductDetailSerializer,
    ProductListSerializer,
)


@api_view(["GET"])
@permission_classes([AllowAny])
def products_list(request):
    """
    Endpoint para listar produtos.
    Pode filtrar por loja se o parâmetro 'store' for fornecido.

    Parâmetros:
    - store: slug da loja (opcional)

    Retorna:
    - Lista de produtos
    """
    # Filtra por loja se fornecido
    store_slug = request.query_params.get("store", None)
    if store_slug:
        products = Product.objects.filter(store__slug=store_slug, store__is_active=True)
    else:
        products = Product.objects.filter(featured=True, store__is_active=True)

    serializer = ProductListSerializer(products, many=True)
    return Response(serializer.data)


@api_view(["GET"])
@permission_classes([AllowAny])
def product_detail(request, slug):
    """
    Endpoint para obter detalhes de um produto.

    Parâmetros:
    - slug: slug do produto

    Retorna:
    - Detalhes do produto ou mensagem de erro
    """
    try:
        product = Product.objects.get(slug=slug, store__is_active=True)
        serializer = ProductDetailSerializer(product)
        return Response(serializer.data)
    except Product.DoesNotExist:
        return Response(
            {"error": "Produto não encontrado"}, status=status.HTTP_404_NOT_FOUND
        )


@api_view(["GET"])
@permission_classes([AllowAny])
def category_list(request):
    """
    Endpoint para listar categorias.

    Retorna:
    - Lista de categorias
    """
    categories = Category.objects.all()
    serializer = CategoryListSerializer(categories, many=True)
    return Response(serializer.data)


@api_view(["GET"])
@permission_classes([AllowAny])
def category_detail(request, slug):
    """
    Endpoint para obter detalhes de uma categoria.

    Parâmetros:
    - slug: slug da categoria

    Retorna:
    - Detalhes da categoria ou mensagem de erro
    """
    try:
        category = Category.objects.get(slug=slug)
        serializer = CategoryDetailSerializer(category)
        return Response(serializer.data)
    except Category.DoesNotExist:
        return Response(
            {"error": "Categoria não encontrada"}, status=status.HTTP_404_NOT_FOUND
        )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_product(request):
    """
    Endpoint para criação de novos produtos.
    Apenas vendedores aprovados com lojas ativas podem criar produtos.

    Parâmetros:
    - Dados do produto no corpo da requisição

    Retorna:
    - Dados do produto criado ou mensagem de erro
    """
    # Verifica se o usuário é um vendedor
    if request.user.user_type != "seller":
        return Response(
            {"error": "Apenas vendedores podem criar produtos."},
            status=status.HTTP_403_FORBIDDEN,
        )

    # Verifica se o vendedor está aprovado e se a loja está ativa
    if (
        not request.user.is_approved_seller
        or not hasattr(request.user, "store")
        or not request.user.store.is_active
    ):
        return Response(
            {"error": "Sua loja não está ativa ou não foi aprovada ainda."},
            status=status.HTTP_403_FORBIDDEN,
        )

    serializer = ProductCreateSerializer(
        data=request.data, context={"request": request}
    )
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["PUT", "DELETE"])
@permission_classes([IsAuthenticated])
def manage_product(request, slug):
    """
    Endpoint para gerenciamento de produtos.
    Permite atualizar ou excluir produtos do usuário.

    Parâmetros:
    - slug: slug do produto

    Retorna:
    - Dados do produto atualizado ou mensagem de sucesso/erro
    """
    try:
        product = Product.objects.get(slug=slug)

        # Verifica se o produto pertence à loja do usuário
        if not hasattr(request.user, "store") or product.store != request.user.store:
            return Response(
                {"error": "Você não tem permissão para modificar este produto."},
                status=status.HTTP_403_FORBIDDEN,
            )

        if request.method == "PUT":
            serializer = ProductCreateSerializer(
                product, data=request.data, partial=True
            )
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        elif request.method == "DELETE":
            product.delete()
            return Response(
                {"message": "Produto excluído com sucesso."},
                status=status.HTTP_204_NO_CONTENT,
            )

    except Product.DoesNotExist:
        return Response(
            {"error": "Produto não encontrado."}, status=status.HTTP_404_NOT_FOUND
        )


@api_view(["GET"])
@permission_classes([AllowAny])
def product_search(request):
    """
    Endpoint para busca de produtos.
    Busca por nome, descrição ou categoria.

    Parâmetros:
    - query: termo de busca

    Retorna:
    - Lista de produtos correspondentes à busca
    """
    query = request.query_params.get("query")
    if not query:
        return Response(
            {"error": "Nenhum termo de busca fornecido."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    products = Product.objects.filter(
        Q(name__icontains=query)
        | Q(description__icontains=query)
        | Q(category__name__icontains=query),
        store__is_active=True,
    )

    serializer = ProductListSerializer(products, many=True)
    return Response(serializer.data)


@api_view(["GET"])
@permission_classes([AllowAny])
def store_products(request, slug):
    """
    Endpoint para listar produtos de uma loja específica.

    Parâmetros:
    - slug: slug da loja

    Retorna:
    - Lista de produtos da loja ou mensagem de erro
    """
    try:
        store = Store.objects.get(slug=slug, is_active=True)
        products = Product.objects.filter(store=store)
        serializer = ProductListSerializer(products, many=True)
        return Response(serializer.data)
    except Store.DoesNotExist:
        return Response(
            {"error": "Loja não encontrada."}, status=status.HTTP_404_NOT_FOUND
        )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def seller_products_list(request):
    """Listar produtos do vendedor autenticado"""
    if request.user.user_type != "seller":
        return Response({"error": "Apenas vendedores"}, status=403)

    products = Product.objects.filter(store__user=request.user)
    serializer = ProductListSerializer(products, many=True)
    return Response(serializer.data)
