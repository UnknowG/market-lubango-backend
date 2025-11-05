from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken
from .models import Store

User = get_user_model()


class UserModelTest(TestCase):
    """Testes para o modelo CustomUser"""

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
        """Configuração inicial para os testes"""
        self.seller = User.objects.create_user(
            username="seller",
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
    
    def test_user_login(self):
        """Testa o login de um usuário"""
        url = reverse("token_obtain_pair")
        login_data = {
            "username": "testuser",
            "password": "testpass123"
        }
        response = self.client.post(url, login_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)
        self.assertIn("user", response.data)

    def test_user_login_with_email(self):
        """Testa o login usando email em vez de username"""
        url = reverse("token_obtain_pair")
        login_data = {
            "username": "test@example.com",  # Usando email
            "password": "testpass123"
        }
        response = self.client.post(url, login_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)

    def test_user_logout(self):
        """Testa o logout de um usuário"""
        # Primeiro faz login para obter o token
        url = reverse("token_obtain_pair")
        login_data = {
            "username": "testuser",
            "password": "testpass123"
        }
        response = self.client.post(url, login_data, format="json")
        refresh_token = response.data["refresh"]
        
        # Agora faz logout
        url = reverse("logout")
        logout_data = {"refresh": refresh_token}
        response = self.client.post(url, logout_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_get_user_profile(self):
        """Testa a obtenção do perfil do usuário"""
        # Autentica o usuário
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        
        # Obtém o perfil
        url = reverse("user_profile")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["username"], self.user_data["username"])
        self.assertEqual(response.data["email"], self.user_data["email"])


class StoreAPITest(APITestCase):
    """Testes para os endpoints de loja"""
    
    def setUp(self):
        """Configuração inicial para os testes"""
        self.seller = User.objects.create_user(
            username="seller",
            email="seller@example.com",
            password="sellerpass123",
            user_type="seller"
        )
        self.buyer = User.objects.create_user(
            username="buyer",
            email="buyer@example.com",
            password="buyerpass123",
            user_type="buyer"
        )
        self.admin = User.objects.create_user(
            username="admin",
            email="admin@example.com",
            password="adminpass123",
            user_type="admin"
        )
    
    def test_create_store_as_seller(self):
        """Testa a criação de uma loja por um vendedor"""
        # Autentica o vendedor
        refresh = RefreshToken.for_user(self.seller)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        
        # Cria a loja
        url = reverse("create_store")
        store_data = {
            "name": "Test Store",
            "description": "A test store"
        }
        response = self.client.post(url, store_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["name"], "Test Store")
        self.assertEqual(response.data["owner"]["id"], self.seller.id)
    
    def test_create_store_as_buyer(self):
        """Testa a tentativa de criação de loja por um comprador (deve falhar)"""
        # Autentica o comprador
        refresh = RefreshToken.for_user(self.buyer)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        
        # Tenta criar a loja
        url = reverse("create_store")
        store_data = {
            "name": "Test Store",
            "description": "A test store"
        }
        response = self.client.post(url, store_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_create_duplicate_store(self):
        """Testa a tentativa de criação de loja duplicada (deve falhar)"""
        # Cria a primeira loja
        Store.objects.create(
            name="Test Store",
            description="A test store",
            owner=self.seller
        )
        
        # Autentica o vendedor
        refresh = RefreshToken.for_user(self.seller)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        
        # Tenta criar a segunda loja
        url = reverse("create_store")
        store_data = {
            "name": "Another Store",
            "description": "Another test store"
        }
        response = self.client.post(url, store_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_get_store(self):
        """Testa a obtenção de dados da loja"""
        # Cria a loja
        store = Store.objects.create(
            name="Test Store",
            description="A test store",
            owner=self.seller
        )
        
        # Autentica o vendedor
        refresh = RefreshToken.for_user(self.seller)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        
        # Obtém os dados da loja
        url = reverse("manage_store")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "Test Store")
    
    def test_update_store(self):
        """Testa a atualização de dados da loja"""
        # Cria a loja
        store = Store.objects.create(
            name="Test Store",
            description="A test store",
            owner=self.seller
        )
        
        # Autentica o vendedor
        refresh = RefreshToken.for_user(self.seller)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        
        # Atualiza os dados da loja
        url = reverse("manage_store")
        update_data = {
            "name": "Updated Store",
            "description": "An updated test store"
        }
        response = self.client.put(url, update_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "Updated Store")
        
        # Verifica se os dados foram atualizados no banco
        store.refresh_from_db()
        self.assertEqual(store.name, "Updated Store")
        self.assertEqual(store.description, "An updated test store")
    
    def test_get_pending_sellers_as_admin(self):
        """Testa a obtenção de vendedores pendentes por um administrador"""
        # Cria um vendedor pendente
        pending_seller = User.objects.create_user(
            username="pending_seller",
            email="pending@example.com",
            password="pendingpass123",
            user_type="seller",
            is_approved_seller=False
        )
        
        # Autentica o administrador
        refresh = RefreshToken.for_user(self.admin)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        
        # Obtém a lista de vendedores pendentes
        url = reverse("pending_sellers")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["id"], pending_seller.id)
    
    def test_get_pending_sellers_as_buyer(self):
        """Testa a tentativa de obtenção de vendedores pendentes por um comprador (deve falhar)"""
        # Autentica o comprador
        refresh = RefreshToken.for_user(self.buyer)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        
        # Tenta obter a lista de vendedores pendentes
        url = reverse("pending_sellers")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_approve_seller_as_admin(self):
        """Testa a aprovação de um vendedor por um administrador"""
        # Cria um vendedor pendente
        pending_seller = User.objects.create_user(
            username="pending_seller",
            email="pending@example.com",
            password="pendingpass123",
            user_type="seller",
            is_approved_seller=False
        )
        
        # Autentica o administrador
        refresh = RefreshToken.for_user(self.admin)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        
        # Aprova o vendedor
        url = reverse("approve_seller", kwargs={"user_id": pending_seller.id})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verifica se o vendedor foi aprovado
        pending_seller.refresh_from_db()
        self.assertTrue(pending_seller.is_approved_seller)
    
    def test_approve_seller_as_buyer(self):
        """Testa a tentativa de aprovação de um vendedor por um comprador (deve falhar)"""
        # Cria um vendedor pendente
        pending_seller = User.objects.create_user(
            username="pending_seller",
            email="pending@example.com",
            password="pendingpass123",
            user_type="seller",
            is_approved_seller=False
        )
        
        # Autentica o comprador
        refresh = RefreshToken.for_user(self.buyer)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        
        # Tenta aprovar o vendedor
        url = reverse("approve_seller", kwargs={"user_id": pending_seller.id})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
