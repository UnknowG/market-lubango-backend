from django.test import TestCase
from django.contrib.auth import get_user_model

User = get_user_model()


class UserModelTests(TestCase):
    """Testes para o modelo CustomUser."""

    def setUp(self):
        """Configuração inicial para os testes"""
        self.user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "testpass123",
            "first_name": "Test",
            "last_name": "User",
            "user_type": "buyer"
        }
