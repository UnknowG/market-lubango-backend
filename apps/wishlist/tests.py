from django.test import TestCase
from django.contrib.auth import get_user_model
from .models import Wishlist
from apps.products.models import Category, Product

User = get_user_model()


class WishlistModelTest(TestCase):
    """Testes para o modelo Wishlist"""

    def setUp(self):
        """Configuração inicial para os testes"""

        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
        )
        self.category = Category.objects.create(name="Test Category")
        self.product = Product.objects.create(
            name="Test Product",
            price=10.99,
            category=self.category,
        )
        self.wishlist_item = Wishlist.objects.create(
            user=self.user,
            product=self.product,
        )
