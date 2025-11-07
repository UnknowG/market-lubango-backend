from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from apps.accounts.models import Store
from .models import Category, Product

User = get_user_model()


class CategoryModelTest(TestCase):
    """Testes para o modelo Category"""

    def test_create_category(self):
        """Testa a criação de uma categoria"""

        category = Category.objects.create(
            name="Test Category",
        )
        self.assertEqual(category.name, "Test Category")
        self.assertTrue(category.slug)  # Verifica se o slug foi gerado automaticamente


class ProductModelTest(TestCase):
    """Testes para o modelo Product"""

    def setUp(self):
        """Configuração inicial para os testes"""
        self.seller = User.objects.create_user(
            username="seller",
            email="seller@example.com",
            password="sellerpass123",
            user_type="seller",
            is_approved_seller=True,
        )
        self.store = Store.objects.create(
            name="Test Store", description="A test store", owner=self.seller
        )
        self.category = Category.objects.create(
            name="Test Category",
        )
        self.product = Product.objects.create(
            name="Test Product",
            description="A test product",
            price=10.99,
            category=self.category,
            store=self.store,
            featured=True,
        )

    def test_products_list(self):
        """Testa a listagem de produtos"""
        url = reverse("product_list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["name"], "Test Product")

    def test_products_list_by_store(self):
        """Testa a listagem de produtos de uma loja específica"""
        url = reverse("product_list")
        response = self.client.get(url, {"store": self.store.slug})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["name"], "Test Product")

    def test_product_detail(self):
        """Testa a obtenção de detalhes de um produto"""
        url = reverse("product_detail", kwargs={"slug": self.product.slug})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "Test Product")
        self.assertEqual(response.data["price"], "10.99")

    def test_product_detail_not_found(self):
        """Testa a tentativa de obter detalhes de um produto inexistente"""
        url = reverse("product_detail", kwargs={"slug": "nonexistent-product"})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_category_list(self):
        """Testa a listagem de categorias"""
        url = reverse("category_list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["name"], "Test Category")

    def test_category_detail(self):
        """Testa a obtenção de detalhes de uma categoria"""
        url = reverse("category_detail", kwargs={"slug": self.category.slug})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "Test Category")
        self.assertEqual(len(response.data["products"]), 1)

    def test_create_product_as_seller(self):
        """Testa a criação de um produto por um vendedor"""
        # Autentica o vendedor
        refresh = RefreshToken.for_user(self.seller)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")

        # Cria o produto
        url = reverse("create_product")
        product_data = {
            "name": "New Product",
            "description": "A new product",
            "price": 15.99,
            "category": self.category.id,
            "in_stock": True,
            "stock_quantity": 10,
        }
        response = self.client.post(url, product_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["name"], "New Product")
        self.assertEqual(response.data["store"], self.store.id)

    def test_create_product_as_buyer(self):
        """Testa a tentativa de criação de um produto por um comprador (deve falhar)"""
        # Autentica o comprador
        refresh = RefreshToken.for_user(self.buyer)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")

        # Tenta criar o produto
        url = reverse("create_product")
        product_data = {
            "name": "New Product",
            "description": "A new product",
            "price": 15.99,
            "category": self.category.id,
            "in_stock": True,
            "stock_quantity": 10,
        }
        response = self.client.post(url, product_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_product_unapproved_seller(self):
        """Testa a tentativa de criação de um produto por um vendedor não aprovado (deve falhar)"""
        # Cria um vendedor não aprovado
        unapproved_seller = User.objects.create_user(
            username="unapproved_seller",
            email="unapproved@example.com",
            password="unapprovedpass123",
            user_type="seller",
            is_approved_seller=False,
        )

        # Autentica o vendedor não aprovado
        refresh = RefreshToken.for_user(unapproved_seller)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")

        # Tenta criar o produto
        url = reverse("create_product")
        product_data = {
            "name": "New Product",
            "description": "A new product",
            "price": 15.99,
            "category": self.category.id,
            "in_stock": True,
            "stock_quantity": 10,
        }
        response = self.client.post(url, product_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_product(self):
        """Testa a atualização de um produto"""
        # Autentica o vendedor
        refresh = RefreshToken.for_user(self.seller)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")

        # Atualiza o produto
        url = reverse("manage_product", kwargs={"slug": self.product.slug})
        update_data = {"name": "Updated Product", "price": 20.99}
        response = self.client.put(url, update_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "Updated Product")
        self.assertEqual(response.data["price"], "20.99")

        # Verifica se os dados foram atualizados no banco
        self.product.refresh_from_db()
        self.assertEqual(self.product.name, "Updated Product")
        self.assertEqual(float(self.product.price), 20.99)

    def test_update_product_by_wrong_owner(self):
        """Testa a tentativa de atualização de um produto por outro usuário (deve falhar)"""
        # Cria outro vendedor
        other_seller = User.objects.create_user(
            username="other_seller",
            email="other@example.com",
            password="otherpass123",
            user_type="seller",
            is_approved_seller=True,
        )

        # Autentica o outro vendedor
        refresh = RefreshToken.for_user(other_seller)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")

        # Tenta atualizar o produto
        url = reverse("manage_product", kwargs={"slug": self.product.slug})
        update_data = {"name": "Updated Product", "price": 20.99}
        response = self.client.put(url, update_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_product(self):
        """Testa a exclusão de um produto"""
        # Autentica o vendedor
        refresh = RefreshToken.for_user(self.seller)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")

        # Exclui o produto
        url = reverse("manage_product", kwargs={"slug": self.product.slug})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # Verifica se o produto foi excluído
        with self.assertRaises(Product.DoesNotExist):
            Product.objects.get(slug=self.product.slug)

    def test_product_search(self):
        """Testa a busca de produtos"""
        # Cria mais produtos para teste
        Product.objects.create(
            name="Another Product",
            description="Another test product",
            price=12.99,
            category=self.category,
            store=self.store,
        )
        Product.objects.create(
            name="Different Item",
            description="A different item for testing",
            price=8.99,
            category=self.category,
            store=self.store,
        )

        # Busca por nome
        url = reverse("search")
        response = self.client.get(url, {"query": "Product"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)  # "Test Product" e "Another Product"

        # Busca por descrição
        url = reverse("search")
        response = self.client.get(url, {"query": "different"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)  # Apenas "Different Item"

        # Busca por categoria
        url = reverse("search")
        response = self.client.get(url, {"query": "Test Category"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)  # Todos os produtos

    def test_store_products(self):
        """Testa a listagem de produtos de uma loja"""
        # Cria mais produtos
        Product.objects.create(
            name="Another Product",
            description="Another test product",
            price=12.99,
            category=self.category,
            store=self.store,
        )

        # Obtém os produtos da loja
        url = reverse("store_products", kwargs={"slug": self.store.slug})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)  # "Test Product" e "Another Product"

    def test_store_products_not_found(self):
        """Testa a tentativa de obter produtos de uma loja inexistente"""
        url = reverse("store_products", kwargs={"slug": "nonexistent-store"})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
