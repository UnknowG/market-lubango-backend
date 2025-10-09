from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from .models import Store
from .serializers import CustomTokenObtainPairSerializer, StoreSerializer, UserRegistrationSerializer, UserSerializer



User = get_user_model()

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


@api_view(["POST"])
@permission_classes([AllowAny])
def register(request):
    serializer = UserRegistrationSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        return Response(
            {"message": "User created successfully."},
            status=status.HTTP_201_CREATED
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def logout(request):
    try:
        refresh_token = request.data.get("refresh")
        if refresh_token:
            token = RefreshToken(refresh_token)
            token.blacklist()
        return Response(
            {"message": "Succesfully logged out."},
            status=status.HTTP_200_OK
        )
    except Exception as e:
        return Response(
            {"error": str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_user_profile(request):
    user = request.user
    serializer = UserSerializer(user)
    return Response(serializer.data)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def  create_store(request):
    # Only seller can create a store
    if request.user.user_type != "seller":
        return Response(
            {"error": "Only sellers can create stores"},
            status=status.HTTP_403_FORBIDDEN
        )
    
    # Check if user already has a store
    if hasattr(request.user, "store"):
        return Response(
            {"error": "You already have a store"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    serializer = StoreSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(owner=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET", "PUT"])
@permission_classes([IsAuthenticated])
def manage_store(request):
    try:
        store = request.user.store
    except Store.DoesNotExist:
        return Response(
            {"error": "Store not found"},
            status=status.HTTP_404_NOT_FOUND
        )
    
    if request.method == "GET":
        serializer = StoreSerializer(store)
        return Response(serializer.data)
    
    elif request.method == "PUT":
        serializer = StoreSerializer(store, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Admin views
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_pending_sellers(request):
    # Only admin can access this view
    if not request.user.user_type != "admin":
        return Response(
            {"error": "Permission denied"},
            status=status.HTTP_403_FORBIDDEN
        )
    
    pending_sellers = User.objects.filter(user_types="seller", is_approved_seller=False)
    serializer = UserSerializer(pending_sellers, many=True)
    return Response(serializer.data)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def approve_seller(request, user_id):
    # Only admins can access this view
    if request.user.user_type != "admin":
        return Response(
            {"error": "Permission denied"},
            status=status.HTTP_403_FORBIDDEN
        )
    
    try:
        seller = User.objects.get(id=user_id, user_type='seller')
        seller.is_approved_seller = True
        seller.save()

        # Activate the store if it exists
        if hasattr(seller, "store"):
            seller.store.is_active = True
            seller.store.save()
        
        return Response({"message": "Seller approved successfully"})
    except User.DoesNotExist:
        return Response(
            {"error": "Seller not found"},
            status=status.HTTP_404_NOT_FOUND
        )
