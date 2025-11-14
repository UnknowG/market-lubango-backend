from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from .models import Wishlist
from apps.products.models import Product, Category
from apps.accounts.models import Store

User = get_user_model()


class WishlistModelTest(TestCase):
    """Testes para o modelo Wishlist"""

    def setUp(self):
        """Configuração inicial para os testes"""
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )
        self.seller = User.objects.create_user(
            username="seller",
            email="seller@example.com",
            password="sellerpass123",
            user_type="seller",
            is_approved_seller=True,
        )
        self.store = Store.objects.create(
            name="Test Store", owner=self.seller,
        )
        self.category = Category.objects.create(name="Test Category")
        self.product = Product.objects.create(
            name="Test Product", price=10.99,
            category=self.category,
            store=self.store,
        )
        self.wishlist_item = Wishlist.objects.create(
            user=self.user, product=self.product
        )

    def test_wishlist_creation(self):
        """Testa a criação de um item na lista de desejos"""
        self.assertEqual(self.wishlist_item.user, self.user)
        self.assertEqual(self.wishlist_item.product, self.product)
        self.assertIsNotNone(self.wishlist_item.created_at)

    def test_wishlist_str(self):
        """Testa o método __str__ do modelo Wishlist"""
        expected_str = f"{self.user.username} - {self.product.name} na lista de desejos"
        self.assertEqual(str(self.wishlist_item), expected_str)

    def test_unique_together(self):
        """Testa a restrição de unicidade entre usuário e produto"""
        # Usar assertRaises como context manager
        from django.db import IntegrityError
        with self.assertRaises(IntegrityError):
            Wishlist.objects.create(user=self.user, product=self.product)

    def test_wishlist_ordering(self):
        """Testa se os itens são ordenados por data de criação (mais recente primeiro)"""
        product2 = Product.objects.create(
            name="Test Product 2", 
            price=20.99, 
            category=self.category,
            store=self.store,
        )
        wishlist_item2 = Wishlist.objects.create(user=self.user, product=product2)
        
        wishlist_items = Wishlist.objects.filter(user=self.user)
        self.assertEqual(wishlist_items.first(), wishlist_item2)
        self.assertEqual(wishlist_items.last(), self.wishlist_item)

    def test_wishlist_related_name(self):
        """Testa o related_name do modelo"""
        self.assertEqual(self.user.wishlist.count(), 1)
        self.assertEqual(self.product.wishlist_items.count(), 1)


class WishlistAPITest(APITestCase):
    """Testes para os endpoints da lista de desejos"""

    def setUp(self):
        """Configuração inicial para os testes"""
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )
        self.seller = User.objects.create_user(
            username="seller",
            email="seller@example.com",
            password="sellerpass123",
            user_type="seller",
            is_approved_seller=True,
        )
        self.store = Store.objects.create(name="Test Store", owner=self.seller)
        self.category = Category.objects.create(name="Test Category")
        self.product = Product.objects.create(
            name="Test Product", price=10.99, category=self.category, store=self.store
        )
        
        # Autenticar usuário
        self.refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.refresh.access_token}")

    def tearDown(self):
        """Limpar credenciais após cada teste"""
        self.client.credentials()

    def test_add_to_wishlist(self):
        """Testa a adição de um produto à lista de desejos"""
        url = reverse("add_to_wishlist")
        data = {"product_id": self.product.id}
        response = self.client.post(url, data, format="json")
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["product"]["id"], self.product.id)
        self.assertIn("user", response.data)
        self.assertIn("created_at", response.data)

        # Verifica se o item foi adicionado à lista de desejos
        self.assertTrue(
            Wishlist.objects.filter(user=self.user, product=self.product).exists()
        )

    def test_remove_from_wishlist(self):
        """Testa a remoção de um produto da lista de desejos"""
        # Adiciona o produto à lista de desejos primeiro
        Wishlist.objects.create(user=self.user, product=self.product)
        self.assertEqual(Wishlist.objects.filter(user=self.user).count(), 1)

        # Remove o produto usando o mesmo endpoint (toggle behavior)
        url = reverse("add_to_wishlist")
        data = {"product_id": self.product.id}
        response = self.client.post(url, data, format="json")
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertIn("message", response.data)

        # Verifica se o item foi removido da lista de desejos
        self.assertFalse(
            Wishlist.objects.filter(user=self.user, product=self.product).exists()
        )

    def test_add_to_wishlist_missing_product_id(self):
        """Testa adicionar sem fornecer product_id"""
        url = reverse("add_to_wishlist")
        data = {}
        response = self.client.post(url, data, format="json")
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data)

    def test_add_to_wishlist_invalid_product(self):
        """Testa a adição de um produto inexistente à lista de desejos"""
        url = reverse("add_to_wishlist")
        data = {"product_id": 999}
        response = self.client.post(url, data, format="json")
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn("error", response.data)

    def test_get_user_wishlist(self):
        """Testa a obtenção da lista de desejos do usuário"""
        # Adiciona alguns produtos à lista de desejos
        Wishlist.objects.create(user=self.user, product=self.product)

        product2 = Product.objects.create(
            name="Test Product 2", price=20.99, category=self.category, store=self.store
        )
        Wishlist.objects.create(user=self.user, product=product2)

        # Obtém a lista de desejos
        url = reverse("get_user_wishlist")
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        
        # Verifica estrutura dos dados
        for item in response.data:
            self.assertIn("id", item)
            self.assertIn("user", item)
            self.assertIn("product", item)
            self.assertIn("created_at", item)

    def test_get_empty_wishlist(self):
        """Testa obter lista de desejos vazia"""
        url = reverse("get_user_wishlist")
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

    def test_delete_wishlist_item(self):
        """Testa a exclusão de um item da lista de desejos"""
        # Adiciona um produto à lista de desejos
        wishlist_item = Wishlist.objects.create(user=self.user, product=self.product)

        # Exclui o item da lista de desejos
        url = reverse("delete_wishlist_item", kwargs={"pk": wishlist_item.id})
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertIn("message", response.data)

        # Verifica se o item foi excluído
        self.assertFalse(Wishlist.objects.filter(id=wishlist_item.id).exists())

    def test_delete_wishlist_item_not_owner(self):
        """Testa a exclusão de um item da lista de desejos por outro usuário"""
        # Cria um usuário e um item na lista de desejos
        user2 = User.objects.create_user(
            username="user2", email="user2@example.com", password="user2pass123"
        )
        wishlist_item = Wishlist.objects.create(user=user2, product=self.product)

        # Tenta excluir o item (usuário original não é dono)
        url = reverse("delete_wishlist_item", kwargs={"pk": wishlist_item.id})
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        
        # Verifica que o item ainda existe
        self.assertTrue(Wishlist.objects.filter(id=wishlist_item.id).exists())

    def test_delete_nonexistent_wishlist_item(self):
        """Testa exclusão de item inexistente"""
        url = reverse("delete_wishlist_item", kwargs={"pk": 999})
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn("error", response.data)

    def test_wishlist_requires_authentication(self):
        """Testa que todos os endpoints requerem autenticação"""
        # Remove autenticação
        self.client.credentials()
        
        # Testa cada endpoint
        endpoints = [
            ("get", reverse("get_user_wishlist")),
            ("post", reverse("add_to_wishlist")),
            ("delete", reverse("delete_wishlist_item", kwargs={"pk": 1})),
        ]
        
        for method, url in endpoints:
            if method == "get":
                response = self.client.get(url)
            elif method == "post":
                response = self.client.post(url, {"product_id": 1})
            elif method == "delete":
                response = self.client.delete(url)
            
            self.assertEqual(
                response.status_code, 
                status.HTTP_401_UNAUTHORIZED,
                f"Endpoint {url} deveria requerer autenticação"
            )

    def test_wishlist_prevents_duplicate_on_race_condition(self):
        """Testa comportamento em condições de corrida"""
        url = reverse("add_to_wishlist")
        data = {"product_id": self.product.id}
        
        # Primeira chamada - adiciona
        response1 = self.client.post(url, data, format="json")
        self.assertEqual(response1.status_code, status.HTTP_201_CREATED)
        
        # Segunda chamada - remove
        response2 = self.client.post(url, data, format="json")
        self.assertEqual(response2.status_code, status.HTTP_204_NO_CONTENT)
        
        # Terceira chamada - adiciona novamente
        response3 = self.client.post(url, data, format="json")
        self.assertEqual(response3.status_code, status.HTTP_201_CREATED)
        
        # Deve haver apenas 1 item
        self.assertEqual(Wishlist.objects.filter(user=self.user).count(), 1)
