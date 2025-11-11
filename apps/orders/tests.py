from django.test import TestCase
from django.contrib.auth import get_user_model
from .models import Order, OrderItem
from apps.products.models import Category, Product

User = get_user_model()


class OrderModelTest(TestCase):
    """Testes para o modelo Order"""

    def setUp(self):
        """Configuração inicial para os testes"""

        self.user = User.objects.create_user(
            sername="testuser",
            email="test@example.com",
            password="testpass123",
        )
        self.order = Order.objects.create(
            user=self.user,
            total_amount=100.00,
            shipping_address="Test Address",
        )
        self.category = Category.objects.create(name="Test Category")
        self.product = Product.objects.create(
            name="Test Product",
            price=10.99,
            category=self.category,
        )
        self.order_item = OrderItem.objects.create(
            order=self.order,
            product=self.product,
            quantity=2,
            price=10.99,
        )
    
    def test_order_item_creation(self):
        """Testa a criação de um item de pedido"""

        self.assertEqual(self.order_item.order, self.order)
        self.assertEqual(self.order_item.product, self.product)
        self.assertEqual(self.order_item.quantity, 2)
        self.assertEqual(self.order_item.price, 10.99)
    
    def test_order_item_str(self):
        """Testa o método __str__ do modelo OrderItem"""
        expected_str = f"2 x {self.product.name} pedido: {self.order.order_number}."
        self.assertEqual(str(self.order_item), expected_str)
