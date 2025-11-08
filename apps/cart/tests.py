from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken
from .models import Cart, CartItem
from apps.products.models import Product, Category

User = get_user_model()

class CartModelTest(TestCase):
    """Testes para o modelo Cart"""
    
    def setUp(self):
        """Configuração inicial para os testes"""
        self.cart = Cart.objects.create(cart_code="TEST12345678")
    
    def test_cart_creation(self):
        """Testa a criação de um carrinho"""
        self.assertEqual(self.cart.cart_code, "TEST12345678")
        self.assertIsNotNone(self.cart.created_at)
        self.assertIsNotNone(self.cart.updated_at)
    
    def test_cart_str(self):
        """Testa o método __str__ do modelo Cart"""
        self.assertEqual(str(self.cart), "TEST12345678")


class CartItemModelTest(TestCase):
    """Testes para o modelo CartItem"""
    
    def setUp(self):
        """Configuração inicial para os testes"""
        self.cart = Cart.objects.create(cart_code="TEST12345678")
        self.category = Category.objects.create(name="Test Category")
        self.product = Product.objects.create(
            name="Test Product",
            price=10.99,
            category=self.category
        )
        self.cart_item = CartItem.objects.create(
            cart=self.cart,
            product=self.product,
            quantity=2
        )
    
    def test_cart_item_creation(self):
        """Testa a criação de um item do carrinho"""
        self.assertEqual(self.cart_item.cart, self.cart)
        self.assertEqual(self.cart_item.product, self.product)
        self.assertEqual(self.cart_item.quantity, 2)
    
    def test_cart_item_str(self):
        """Testa o método __str__ do modelo CartItem"""
        expected_str = f"2 x {self.product.name} in cart {self.cart.cart_code}"
        self.assertEqual(str(self.cart_item), expected_str)


class CartAPITest(APITestCase):
    """Testes para os endpoints de carrinho"""
    
    def setUp(self):
        """Configuração inicial para os testes"""
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123"
        )
        self.category = Category.objects.create(name="Test Category")
        self.product = Product.objects.create(
            name="Test Product",
            price=10.99,
            category=self.category,
            stock_quantity=10,
            in_stock=True
        )
        self.cart = Cart.objects.create(cart_code="TEST12345678")
    
    def test_get_cart(self):
        """Testa a obtenção de um carrinho"""
        url = reverse("get_cart", kwargs={"cart_code": self.cart.cart_code})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["cart_code"], self.cart.cart_code)
    
    def test_get_cart_not_found(self):
        """Testa a tentativa de obter um carrinho inexistente"""
        url = reverse("get_cart", kwargs={"cart_code": "NONEXISTENT"})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_create_cart(self):
        """Testa a criação de um novo carrinho"""
        url = reverse("create_cart")
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("cart_code", response.data)
        self.assertEqual(len(response.data["cart_code"]), 11)
    
    def test_add_to_cart(self):
        """Testa a adição de um produto ao carrinho"""
        url = reverse("add_to_cart", kwargs={"cart_code": self.cart.cart_code})
        data = {
            "product_id": self.product.id,
            "quantity": 2
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["cartitems"]), 1)
        self.assertEqual(response.data["cartitems"][0]["quantity"], 2)
    
    def test_add_to_cart_product_not_found(self):
        """Testa a adição de um produto inexistente ao carrinho"""
        url = reverse("add_to_cart", kwargs={"cart_code": self.cart.cart_code})
        data = {
            "product_id": 999,
            "quantity": 2
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_add_to_cart_insufficient_stock(self):
        """Testa a adição de um produto com estoque insuficiente"""
        url = reverse("add_to_cart", kwargs={"cart_code": self.cart.cart_code})
        data = {
            "product_id": self.product.id,
            "quantity": 20  # Mais do que o estoque disponível (10)
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_update_cartitem_quantity(self):
        """Testa a atualização da quantidade de um item no carrinho"""
        # Primeiro adiciona um item ao carrinho
        cart_item = CartItem.objects.create(
            cart=self.cart,
            product=self.product,
            quantity=2
        )
        
        # Autentica o usuário
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        
        # Atualiza a quantidade
        url = reverse("update_cartitem_quantity")
        data = {
            "item_id": cart_item.id,
            "quantity": 5
        }
        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["data"]["quantity"], 5)
    
    def test_update_cartitem_quantity_unauthorized(self):
        """Testa a atualização da quantidade de um item sem autenticação"""
        # Primeiro adiciona um item ao carrinho
        cart_item = CartItem.objects.create(
            cart=self.cart,
            product=self.product,
            quantity=2
        )
        
        # Tenta atualizar a quantidade sem autenticação
        url = reverse("update_cartitem_quantity")
        data = {
            "item_id": cart_item.id,
            "quantity": 5
        }
        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
