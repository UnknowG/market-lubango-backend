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
            store=self.store
        )
        self.wishlist_item = Wishlist.objects.create(
            user=self.user, product=self.product
        )

    def test_wishlist_creation(self):
        """Testa a criação de um item na lista de desejos"""
        self.assertEqual(self.wishlist_item.user, self.user)
        self.assertEqual(self.wishlist_item.product, self.product)

    def test_wishlist_str(self):
        """Testa o método __str__ do modelo Wishlist"""
        expected_str = f"{self.user.username} - {self.product.name} na lista de desejos"
        self.assertEqual(str(self.wishlist_item), expected_str)

    def test_unique_together(self):
        """Testa a restrição de unicidade entre usuário e produto"""
        with self.assertRaises(Exception):
            Wishlist.objects.create(user=self.user, product=self.product)


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

    def test_add_to_wishlist(self):
        """Testa a adição de um produto à lista de desejos"""
        # Autentica o usuário
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")

        # Adiciona o produto à lista de desejos
        url = reverse("add_to_wishlist")
        data = {"product_id": self.product.id}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["product"]["id"], self.product.id)

        # Verifica se o item foi adicionado à lista de desejos
        wishlist_item = Wishlist.objects.get(user=self.user, product=self.product)
        self.assertEqual(wishlist_item.product, self.product)

    def test_remove_from_wishlist(self):
        """Testa a remoção de um produto da lista de desejos"""
        # Adiciona o produto à lista de desejos
        Wishlist.objects.create(user=self.user, product=self.product)

        # Autentica o usuário
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")

        # Remove o produto da lista de desejos
        url = reverse("add_to_wishlist")
        data = {"product_id": self.product.id}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # Verifica se o item foi removido da lista de desejos
        with self.assertRaises(Wishlist.DoesNotExist):
            Wishlist.objects.get(user=self.user, product=self.product)

    def test_add_to_wishlist_invalid_product(self):
        """Testa a adição de um produto inexistente à lista de desejos"""
        # Autentica o usuário
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")

        # Tenta adicionar um produto inexistente
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

        # Autentica o usuário
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")

        # Obtém a lista de desejos
        url = reverse("get_user_wishlist")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_delete_wishlist_item(self):
        """Testa a exclusão de um item da lista de desejos"""
        # Adiciona um produto à lista de desejos
        wishlist_item = Wishlist.objects.create(user=self.user, product=self.product)

        # Autentica o usuário
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")

        # Exclui o item da lista de desejos
        url = reverse("delete_wishlist_item", kwargs={"pk": wishlist_item.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # Verifica se o item foi excluído
        with self.assertRaises(Wishlist.DoesNotExist):
            Wishlist.objects.get(id=wishlist_item.id)

    def test_delete_wishlist_item_not_owner(self):
        """Testa a exclusão de um item da lista de desejos por outro usuário"""
        # Cria um usuário e um item na lista de desejos
        user2 = User.objects.create_user(
            username="user2", email="user2@example.com", password="user2pass123"
        )
        wishlist_item = Wishlist.objects.create(user=user2, product=self.product)

        # Autentica o usuário original
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")

        # Tenta excluir o item
        url = reverse("delete_wishlist_item", kwargs={"pk": wishlist_item.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
