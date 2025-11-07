from django.test import TestCase
from django.contrib.auth import get_user_model
from .models import Category

User = get_user_model()


class CategoryModelTest(TestCase):
    """Testes para o modelo Category"""

    def test_create_category(self):
        """Testa a criação de uma categoria"""

        category = Category.objects.create(
            name="Test Category",
        )
        self.assertEqual(category.name, "Test Category")
        self.assertTrue(category.slug) # Verifica se o slug foi gerado automaticamente
