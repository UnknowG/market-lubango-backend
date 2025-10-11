from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import get_user_model
from .models import Store

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id", "username" ,"first_name", "last_name", "email", "user_type", "avatar_url", "birth_date", "phone"
        ]


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = [
            "username", "first_name", "last_name", "email", "password", "confirm_password", "user_type", "birth_date", "phone"
        ]
    
    def validate(self, attrs):
        if attrs["password"] != attrs["confirm_password"]:
            raise serializers.ValidationError("Passwords don't match.")
        return attrs
    
    def create(self, validated_data):
        validated_data.pop("confirm_password")
        user = User.objects.create_user(**validated_data)
        return user


class StoreSerializer(serializers.ModelSerializer):
    owner = UserSerializer(read_only=True)

    class Meta:
        model = Store
        fields = [
            "id", "name", "slug", "description", "logo", "owner", "is_active"
        ]


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["email"] = user.email
        token["name"] = user.get_full_name() or user.username
        token["user_type"] = user.user_type
        return token
    
    def validate(self, attrs):
        identifier = attrs.get("username")
        password = attrs.get("password")

        if identifier and password:
            try:
                user_obj = User.objects.get(email=identifier)
                # If found by email, set username to email
                attrs["username"] = user_obj.username
            except User.DoesNotExist:
                # If not found by email, proceed with username
                pass

        data = super().validate(attrs)
        data["user"] = {
            "id": self.user.id,
            "email": self.user.email,
            "name": self.user.get_full_name() or self.user.username,
            "user_type": self.user.user_type,
        }
        return data
