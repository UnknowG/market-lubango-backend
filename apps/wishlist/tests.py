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
            Wishlist.objects.create(
                user=self.user,
                product=self.product,
            )
