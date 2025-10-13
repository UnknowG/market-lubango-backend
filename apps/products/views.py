from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.db.models import Q
from .models import Category, Product
from .serializers import CategoryDetailSerializer, CategoryListSerializer, ProductCreateSerializer, ProductDetailSerializer, ProductListSerializer


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


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def create_product(request):
    # Only sellers can create products
    if request.user.user_type != "seller":
        return Response(
            {"error": "Only sellers can create products."},
            status=status.HTTP_403_FORBIDDEN
        )
    
    # Check if seller is approved and store is active
    if not request.user.is_approved or not hasattr(request.user, "store") or not request.user.store.is_active:
        return Response(
            {"error": "Your store is not active or not approved yet."},
            status=status.HTTP_403_FORBIDDEN
        )
    
    serializer = ProductCreateSerializer(data=request.data, context={"request": request})
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["PUT", "DELETE"])
@permission_classes([IsAuthenticated])
def manage_product(request, slug):
    try:
        product = Product.objects.get(slug=slug)

        # Checlk if the product belongs to the user's store
        if not hasattr(request.user, "store") or product.store != request.user.store:
            return Response(
                {"error": "You don't have permission to modify this product."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        if request.method == "PUT":
            serializer = ProductCreateSerializer(product, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        elif request.method == "DELETE":
            product.delete()
            return Response(
                {"message": "Product deleted successfully."},
                status=status.HTTP_204_NO_CONTENT
            )
    
    except Product.DoesNotExist:
        return Response(
            {"error": "Product not found."},
            status=status.HTTP_404_NOT_FOUND
        )

@api_view(["GET"])
@permission_classes([AllowAny])
def product_search(request):
    query = request.query_params.get("query")
    if not query:
        return Response(
            {"error": "No query provided."},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    product = Product.objects.filter(
        Q(name__icontains=query) |
        Q(description__icontains=query) |
        Q(category__name__icontains=query),
        store__is_active=True
    )

    serializer = ProductListSerializer(product, many=True)
    return Response(serializer.data)


@api_view(["GET"])
@permission_classes([AllowAny])
def store_products(request, slug):
    try:
        from accounts.models import Store
        store = Store.objects.get(slug=slug, is_active=True)
        products = Product.objects.filter(store=store)
        serializer = ProductListSerializer(products, many=True)
        return Response(serializer.data)
    except Store.DoesNotExist:
        return Response(
            {"error": "Store not found."},
            status=status.HTTP_404_NOT_FOUND
        )
