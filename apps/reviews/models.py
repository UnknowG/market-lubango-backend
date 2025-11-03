from django.db import models
from django.conf import settings
from apps.products.models import Product


class Review(models.Model):
    RATINGS_CHOICES = [
        (1, "Poor"),
        (2, "Fair"),
        (3, "Good"),
        (4, "Very Good"),
        (5, "Excellent"),
    ]

    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="reviews"
    )
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="reviews")
    rating = models.PositiveIntegerField(choices=RATINGS_CHOICES)
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s review of {self.product.name}"
    
    class Meta:
        unique_together = ["product", "user"]
        ordering = ["-created_at"]


class ProductRating(models.Model):
    product = models.OneToOneField(Product, on_delete=models.CASCADE, related_name="rating")
    average_rating = models.FloatField(default=0.0)
    total_reviews = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.product.name} - {self.average_rating} ({self.total_reviews}) reviews."
