from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from .models import Review, ProductRating
from apps.products.models import Product, Category
from apps.accounts.models import Store
from apps.orders.models import Order, OrderItem

User = get_user_model()


class ReviewModelTest(TestCase):
    """Testes para o modelo Review"""

    def setUp(self):
        """Configuração inicial para os testes"""
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )
        self.category = Category.objects.create(name="Test Category")
        self.product = Product.objects.create(
            name="Test Product", price=10.99, category=self.category
        )
        self.review = Review.objects.create(
            product=self.product, user=self.user, rating=4, comment="Great product!"
        )

    def test_review_creation(self):
        """Testa a criação de uma avaliação"""
        self.assertEqual(self.review.product, self.product)
        self.assertEqual(self.review.user, self.user)
        self.assertEqual(self.review.rating, 4)
        self.assertEqual(self.review.comment, "Great product!")

    def test_review_str(self):
        """Testa o método __str__ do modelo Review"""
        expected_str = f"Avaliação de {self.user.username} para {self.product.name}"
        self.assertEqual(str(self.review), expected_str)

    def test_unique_together(self):
        """Testa a restrição de unicidade entre produto e usuário"""
        with self.assertRaises(Exception):
            Review.objects.create(
                product=self.product, user=self.user, rating=5, comment="Another review"
            )


class ProductRatingModelTest(TestCase):
    """Testes para o modelo ProductRating"""

    def setUp(self):
        """Configuração inicial para os testes"""
        self.category = Category.objects.create(name="Test Category")
        self.product = Product.objects.create(
            name="Test Product", price=10.99, category=self.category
        )
        self.product_rating = ProductRating.objects.create(
            product=self.product, average_rating=4.5, total_reviews=10
        )

    def test_product_rating_creation(self):
        """Testa a criação de uma classificação de produto"""
        self.assertEqual(self.product_rating.product, self.product)
        self.assertEqual(self.product_rating.average_rating, 4.5)
        self.assertEqual(self.product_rating.total_reviews, 10)

    def test_product_rating_str(self):
        """Testa o método __str__ do modelo ProductRating"""
        expected_str = f"{self.product.name} - 4.5 (10) avaliações."
        self.assertEqual(str(self.product_rating), expected_str)


class ReviewAPITest(APITestCase):
    """Testes para os endpoints de avaliações"""

    def setUp(self):
        """Configuração inicial para os testes"""
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )
        self.seller = User.objects.create_user(
            username="seller",
            email="seller@example.com",
            password="sellerpass123",
            user_type="seller",
            is_approved_seller=True,
        )
        self.store = Store.objects.create(name="Test Store", owner=self.seller)
        self.category = Category.objects.create(name="Test Category")
        self.product = Product.objects.create(
            name="Test Product", price=10.99, category=self.category, store=self.store
        )

        # Criar um pedido para o usuário
        self.order = Order.objects.create(
            user=self.user,
            total_amount=10.99,
            shipping_address="Test Address",
            status="delivered",
        )
        OrderItem.objects.create(
            order=self.order, product=self.product, quantity=1, price=10.99
        )

    def test_add_review(self):
        """Testa a adição de uma avaliação"""
        # Autentica o usuário
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")

        # Adiciona a avaliação
        url = reverse("add_review")
        data = {
            "product_id": self.product.id,
            "rating": 5,
            "comment": "Excellent product!",
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["rating"], 5)
        self.assertEqual(response.data["comment"], "Excellent product!")

        # Verifica se a classificação do produto foi atualizada
        product_rating = ProductRating.objects.get(product=self.product)
        self.assertEqual(product_rating.average_rating, 5.0)
        self.assertEqual(product_rating.total_reviews, 1)

    def test_add_review_without_purchase(self):
        """Testa a adição de uma avaliação sem ter comprado o produto"""
        # Cria um usuário que não comprou o produto
        user2 = User.objects.create_user(
            username="user2", email="user2@example.com", password="user2pass123"
        )

        # Autentica o usuário
        refresh = RefreshToken.for_user(user2)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")

        # Tenta adicionar a avaliação
        url = reverse("add_review")
        data = {
            "product_id": self.product.id,
            "rating": 5,
            "comment": "Excellent product!",
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data)

    def test_add_duplicate_review(self):
        """Testa a adição de uma avaliação duplicada"""
        # Cria uma avaliação
        Review.objects.create(
            product=self.product, user=self.user, rating=4, comment="Good product!"
        )

        # Autentica o usuário
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")

        # Tenta adicionar outra avaliação
        url = reverse("add_review")
        data = {
            "product_id": self.product.id,
            "rating": 5,
            "comment": "Excellent product!",
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data)

    def test_update_review(self):
        """Testa a atualização de uma avaliação"""
        # Cria uma avaliação
        review = Review.objects.create(
            product=self.product, user=self.user, rating=4, comment="Good product!"
        )

        # Autentica o usuário
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")

        # Atualiza a avaliação
        url = reverse("update_review", kwargs={"pk": review.id})
        data = {"rating": 5, "comment": "Excellent product!"}
        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["rating"], 5)
        self.assertEqual(response.data["comment"], "Excellent product!")

    def test_update_review_not_owner(self):
        """Testa a atualização de uma avaliação por outro usuário"""
        # Cria um usuário e uma avaliação
        user2 = User.objects.create_user(
            username="user2", email="user2@example.com", password="user2pass123"
        )
        review = Review.objects.create(
            product=self.product, user=user2, rating=4, comment="Good product!"
        )

        # Autentica o usuário original
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")

        # Tenta atualizar a avaliação
        url = reverse("update_review", kwargs={"pk": review.id})
        data = {"rating": 5, "comment": "Excellent product!"}
        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_review(self):
        """Testa a exclusão de uma avaliação"""
        # Cria uma avaliação
        review = Review.objects.create(
            product=self.product, user=self.user, rating=4, comment="Good product!"
        )

        # Autentica o usuário
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")

        # Exclui a avaliação
        url = reverse("delete_review", kwargs={"pk": review.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # Verifica se a avaliação foi excluída
        with self.assertRaises(Review.DoesNotExist):
            Review.objects.get(id=review.id)

    def test_get_product_reviews(self):
        """Testa a obtenção de avaliações de um produto"""
        # Cria algumas avaliações
        Review.objects.create(
            product=self.product, user=self.user, rating=4, comment="Good product!"
        )
        user2 = User.objects.create_user(
            username="user2", email="user2@example.com", password="user2pass123"
        )
        Review.objects.create(
            product=self.product, user=user2, rating=5, comment="Excellent product!"
        )

        # Autentica o usuário
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")

        # Obtém as avaliações
        url = reverse("product_reviews", kwargs={"product_id": self.product.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["reviews"]), 2)
        self.assertEqual(response.data["rating"]["average_rating"], 4.5)
        self.assertEqual(response.data["rating"]["total_reviews"], 2)

    def test_get_user_reviews(self):
        """Testa a obtenção de avaliações do usuário"""
        # Cria algumas avaliações
        Review.objects.create(
            product=self.product, user=self.user, rating=4, comment="Good product!"
        )

        product2 = Product.objects.create(
            name="Test Product 2", price=20.99, category=self.category, store=self.store
        )
        Review.objects.create(
            product=product2, user=self.user, rating=5, comment="Excellent product!"
        )

        # Autentica o usuário
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")

        # Obtém as avaliações
        url = reverse("user_reviews")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_get_store_product_reviews(self):
        """Testa a obtenção de avaliações dos produtos da loja"""
        # Cria algumas avaliações
        Review.objects.create(
            product=self.product, user=self.user, rating=4, comment="Good product!"
        )

        # Autentica o vendedor
        refresh = RefreshToken.for_user(self.seller)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")

        # Obtém as avaliações
        url = reverse("store_reviews")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_get_store_product_reviews_not_seller(self):
        """Testa a obtenção de avaliações por um usuário que não é vendedor"""
        # Autentica o usuário
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")

        # Tenta obter as avaliações
        url = reverse("store_reviews")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn("error", response.data)
