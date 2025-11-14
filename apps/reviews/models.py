from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from apps.products.models import Product


class Review(models.Model):
    """
    Modelo para representar avaliações de produtos.
    """

    RATINGS_CHOICES = [
        (1, "Ruim"),
        (2, "Regular"),
        (3, "Bom"),
        (4, "Muito Bom"),
        (5, "Excelente"),
    ]

    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="reviews"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="reviews"
    )
    rating = models.PositiveIntegerField(
        choices=RATINGS_CHOICES,
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Avaliação de {self.user.username} para {self.product.name}"

    class Meta:
        unique_together = ["product", "user"]
        ordering = ["-created_at"]
        verbose_name = "Avaliação"
        verbose_name_plural = "Avaliações"
        indexes = [
            models.Index(fields=["product", "-created_at"]),
            models.Index(fields=["user", "-created_at"]),
        ]


class ProductRating(models.Model):
    """
    Modelo para armazenar a classificação média de um produto.
    """

    product = models.OneToOneField(
        Product, on_delete=models.CASCADE, related_name="rating"
    )
    average_rating = models.FloatField(
        default=0.0,
        validators=[MinValueValidator(0.0), MaxValueValidator(5.0)]
    )
    total_reviews = models.PositiveIntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.product.name} - {self.average_rating} ({self.total_reviews}) avaliações."

    class Meta:
        verbose_name = "Classificação de Produto"
        verbose_name_plural = "Classificações de Produtos"
