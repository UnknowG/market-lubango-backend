from django.test import TestCase
from .models import Cart

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
