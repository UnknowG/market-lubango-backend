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
