from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from .models import Store

User = get_user_model()


class UserModelTests(TestCase):
    """Testes para o modelo CustomUser."""

    def setUp(self):
        """Configuração inicial para os testes"""
        self.user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "testpass123",
            "first_name": "Test",
            "last_name": "User",
            "user_type": "buyer"
        }
    
    def test_create_user(self):
        """Testa a criação de um usuário comum"""
        user = User.objects.create_user(**self.user_data)
        self.assertEqual(user.username, self.user_data["username"])
        self.assertEqual(user.email, self.user_data["email"])
        self.assertEqual(user.user_type, self.user_data["user_type"])
        self.assertTrue(user.check_password(self.user_data["password"]))
    
    def test_create_superuser(self):
        """Testa a criação de um superusuário"""
        admin_user = User.objects.create_superuser(
            username="admin",
            email="admin@example.com",
            password="adminpass123"
        )
        self.assertEqual(admin_user.username, "admin")
        self.assertEqual(admin_user.email, "admin@example.com")
        self.assertTrue(admin_user.is_staff)
        self.assertTrue(admin_user.is_superuser)


class StoreModelTest(TestCase):
    """Testes para o modelo Store"""

    def setUp(self):
        self.seller = User.objects.create_user(username="seller",
            email="seller@example.com",
            password="sellerpass123",
            user_type="seller"
        )
    
    def test_create_store(self):
        """Testa a criação de uma loja"""
        store = Store.objects.create(
            name="Test Store",
            description="A test store",
            owner=self.seller
        )
        self.assertEqual(store.name, "Test Store")
        self.assertEqual(store.owner, self.seller)
        self.assertTrue(store.slug)  # Verifica se o slug foi gerado automaticamente
        self.assertTrue(store.is_active)


class AuthenticationAPITest(APITestCase):
    """Testes para os endpoints de autenticação"""
    
    def setUp(self):
        """Configuração inicial para os testes"""
        self.user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "testpass123",
            "first_name": "Test",
            "last_name": "User",
            "user_type": "buyer"
        }
        self.user = User.objects.create_user(**self.user_data)
    
    def test_user_registration(self):
        """Testa o registro de um novo usuário"""
        url = reverse("register")
        new_user_data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "newpass123",
            "confirm_password": "newpass123",
            "first_name": "New",
            "last_name": "User",
            "user_type": "buyer"
        }
        response = self.client.post(url, new_user_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 2)
    
    def test_user_registration_password_mismatch(self):
        """Testa o registro com senhas não correspondentes"""
        url = reverse("register")
        new_user_data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "newpass123",
            "confirm_password": "differentpass",
            "first_name": "New",
            "last_name": "User",
            "user_type": "buyer"
        }
        response = self.client.post(url, new_user_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
