from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken
from .models import Order, OrderItem, Payment
from apps.products.models import Category, Product
from apps.accounts.models import Store
from apps.cart.models import Cart, CartItem

User = get_user_model()


class OrderModelTest(TestCase):
    """Testes para o modelo Order"""

    def setUp(self):
        """Configuração inicial para os testes"""

        self.user = User.objects.create_user(
            username="testuser",
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


class PaymentModelTest(TestCase):
    """Testes para o modelo Payment"""

    def setUp(self):
        """Configuração inicial para os testes"""
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )
        self.order = Order.objects.create(
            user=self.user, total_amount=100.00, shipping_address="Test Address"
        )
        self.payment = Payment.objects.create(
            order=self.order, payment_method="reference", amount=100.00
        )

    def test_payment_creation(self):
        """Testa a criação de um pagamento"""
        self.assertEqual(self.payment.order, self.order)
        self.assertEqual(self.payment.payment_method, "reference")
        self.assertEqual(self.payment.amount, 100.00)
        self.assertEqual(self.payment.payment_status, "pending")

    def test_payment_str(self):
        """Testa o método __str__ do modelo Payment"""
        expected_str = f"Pagamento para o pedido: {self.order.order_number}"
        self.assertEqual(str(self.payment), expected_str)


class OrderAPITest(APITestCase):
    """Testes para os endpoints de pedidos"""

    def setUp(self):
        """Configuração inicial para os testes"""
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
        )
        self.seller = User.objects.create_user(
            username="seller",
            email="seller@example.com",
            password="sellerpass123",
            user_type="seller",
            is_approved_seller=True,
        )
        self.store = Store.objects.create(
            name="Test Store",
            owner=self.seller,
        )
        self.category = Category.objects.create(name="Test Category")
        self.product = Product.objects.create(
            name="Test Product",
            price=10.99,
            category=self.category,
            store=self.store,
            stock_quantity=10,
            in_stock=True,
        )
        self.cart = Cart.objects.create(cart_code="TEST12345678")
        CartItem.objects.create(
            cart=self.cart,
            product=self.product,
            quantity=2,
        )

    def test_create_order(self):
        """Testa a criação de um pedido"""

        # Autentica o usuário
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")

        # Cria o pedido
        url = reverse("create_order")
        data = {
            "cart_code": "TEST12345678",
            "shipping_address": "Test Address",
            "payment_method": "reference",
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("order", response.data)
        self.assertIn("message", response.data)

        # Verifica se o pedido foi criado
        order = Order.objects.get(user=self.user)
        self.assertEqual(order.shipping_address, "Test Address")
        self.assertEqual(order.total_amount, 21.98)  # 10.99 * 2

        # Verifica se os itens do pedido foram criados
        self.assertEqual(order.items.count(), 1)
        self.assertEqual(order.items.first().product, self.product)

        # Verifica se o estoque foi atualizado
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock_quantity, 8)  # 10 - 2

    def test_create_order_empty_cart(self):
        """Testa a criação de um pedido com carrinho vazio"""
        # Cria um carrinho vazio
        empty_cart = Cart.objects.create(cart_code="EMPTY12345678")

        # Autentica o usuário
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")

        # Tenta criar o pedido
        url = reverse("create_order")
        data = {
            "cart_code": "EMPTY12345678",
            "shipping_address": "Test Address",
            "payment_method": "reference",
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data)

    def test_create_order_cart_not_found(self):
        """Testa a criação de um pedido com carrinho inexistente"""
        # Autentica o usuário
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")

        # Tenta criar o pedido
        url = reverse("create_order")
        data = {
            "cart_code": "NONEXISTENT",
            "shipping_address": "Test Address",
            "payment_method": "reference",
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn("error", response.data)

    def test_get_user_orders(self):
        """Testa a obtenção dos pedidos do usuário"""
        # Cria alguns pedidos para o usuário
        order1 = Order.objects.create(
            user=self.user, total_amount=100.00, shipping_address="Test Address 1"
        )
        order2 = Order.objects.create(
            user=self.user, total_amount=200.00, shipping_address="Test Address 2"
        )

        # Autentica o usuário
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")

        # Obtém os pedidos
        url = reverse("user_orders")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

        # Verifica se os pedidos estão ordenados por data de criação (mais recente primeiro)
        self.assertEqual(response.data[0]["id"], order2.id)
        self.assertEqual(response.data[1]["id"], order1.id)

    def test_get_order_detail(self):
        """Testa a obtenção de detalhes de um pedido"""
        # Cria um pedido para o usuário
        order = Order.objects.create(
            user=self.user, total_amount=100.00, shipping_address="Test Address"
        )

        # Autentica o usuário
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")

        # Obtém os detalhes do pedido
        url = reverse("order_detail", kwargs={"order_number": order.order_number})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["order_number"], order.order_number)
        self.assertEqual(response.data["total_amount"], "100.00")

    def test_get_order_detail_not_found(self):
        """Testa a obtenção de detalhes de um pedido inexistente"""
        # Autentica o usuário
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")

        # Tenta obter os detalhes do pedido
        url = reverse("order_detail", kwargs={"order_number": "NONEXISTENT"})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn("error", response.data)

    def test_request_refund(self):
        """Testa a solicitação de reembolso"""
        # Cria um pedido para o usuário com pagamento
        order = Order.objects.create(
            user=self.user,
            total_amount=100.00,
            shipping_address="Test Address",
            status="confirmed",
            payment_status="paid",
        )
        Payment.objects.create(
            order=order,
            payment_method="reference",
            payment_status="completed",
            amount=100.00,
        )

        # Autentica o usuário
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")

        # Solicita o reembolso
        url = reverse("request_refund", kwargs={"order_number": order.order_number})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("message", response.data)

    def test_request_refund_not_eligible(self):
        """Testa a solicitação de reembolso para um pedido não elegível"""
        # Cria um pedido para o usuário com status "delivered"
        order = Order.objects.create(
            user=self.user,
            total_amount=100.00,
            shipping_address="Test Address",
            status="delivered",
        )

        # Autentica o usuário
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")

        # Tenta solicitar o reembolso
        url = reverse("request_refund", kwargs={"order_number": order.order_number})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data)

    def test_get_store_orders(self):
        """Testa a obtenção de pedidos para a loja do vendedor"""
        # Cria um pedido com um produto da loja do vendedor
        order = Order.objects.create(
            user=self.user, total_amount=100.00, shipping_address="Test Address"
        )
        OrderItem.objects.create(
            order=order, product=self.product, quantity=2, price=10.99
        )

        # Autentica o vendedor
        refresh = RefreshToken.for_user(self.seller)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")

        # Obtém os pedidos da loja
        url = reverse("store_orders")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["id"], order.id)

    def test_get_store_orders_not_seller(self):
        """Testa a obtenção de pedidos por um usuário que não é vendedor"""
        # Autentica o usuário (que não é vendedor)
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")

        # Tenta obter os pedidos da loja
        url = reverse("store_orders")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn("error", response.data)

    def test_update_order_status(self):
        """Testa a atualização do status de um pedido"""
        # Cria um pedido com um produto da loja do vendedor
        order = Order.objects.create(
            user=self.user, total_amount=100.00, shipping_address="Test Address"
        )
        OrderItem.objects.create(
            order=order, product=self.product, quantity=2, price=10.99
        )

        # Autentica o vendedor
        refresh = RefreshToken.for_user(self.seller)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")

        # Atualiza o status do pedido
        url = reverse(
            "update_order_status", kwargs={"order_number": order.order_number}
        )
        data = {"status": "processing"}
        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], "processing")

        # Verifica se o status foi atualizado no banco
        order.refresh_from_db()
        self.assertEqual(order.status, "processing")

    def test_update_order_status_not_seller(self):
        """Testa a atualização do status de um pedido por um usuário que não é vendedor"""
        # Cria um pedido
        order = Order.objects.create(
            user=self.user, total_amount=100.00, shipping_address="Test Address"
        )

        # Autentica o usuário (que não é vendedor)
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")

        # Tenta atualizar o status do pedido
        url = reverse(
            "update_order_status", kwargs={"order_number": order.order_number}
        )
        data = {"status": "processing"}
        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn("error", response.data)

    def test_update_order_status_invalid_status(self):
        """Testa a atualização do status de um pedido com um status inválido"""
        # Cria um pedido com um produto da loja do vendedor
        order = Order.objects.create(
            user=self.user, total_amount=100.00, shipping_address="Test Address"
        )
        OrderItem.objects.create(
            order=order, product=self.product, quantity=2, price=10.99
        )

        # Autentica o vendedor
        refresh = RefreshToken.for_user(self.seller)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")

        # Tenta atualizar o status do pedido com um status inválido
        url = reverse(
            "update_order_status", kwargs={"order_number": order.order_number}
        )
        data = {"status": "invalid_status"}
        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data)
