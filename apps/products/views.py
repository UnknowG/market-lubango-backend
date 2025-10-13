from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from .models import Category, Product
from .serializers import CategoryDetailSerializer, CategoryListSerializer, ProductDetailSerializer, ProductListSerializer


@api_view(["GET"])
@permission_classes([AllowAny])
def products_list(request):
    # Filter by store if provided
    store_slug = request.query_params.get("store", None)
    if store_slug:
        products = Product.objects.filter(store__slug=store_slug, store__is_active=True)
    else:
        products = Product.objects.filter(feature=True, store__is_active=True)
    
    serializer = ProductListSerializer(products, many=True)
    return Response(serializer.data)


@api_view(["GET"])
@permission_classes([AllowAny])
def product_detail(request, slug):
    try:
        product = Product.objects.get(slug=slug, store__is_active=True)
        serializer = ProductDetailSerializer(product)
        return Response(serializer.data)
    except Product.DoesNotExist:
        return Response(
            {"error": "Product not found"},
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(["GET"])
@permission_classes([AllowAny])
def category_list(request):
    categories = Category.objects.all()
    serializer = CategoryListSerializer(categories, many=True)
    return Response(serializer.data)


@api_view(["GET"])
@permission_classes([AllowAny])
def category_detail(request, slug):
    try:
        category = Category.objects.get(slug=slug)
        serializer = CategoryDetailSerializer(category)
        return Response(serializer.data)
    except Category.DoesNotExist:
        return Response(
            {"error": "Category not found"},
            status=status.HTTP_404_NOT_FOUND
        )
