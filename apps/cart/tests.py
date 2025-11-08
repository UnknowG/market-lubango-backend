from django.test import TestCase
from django.contrib.auth import get_user_model()
from rest_framework.test import APITestCase
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
