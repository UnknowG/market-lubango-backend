from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.db.models import Avg
from .models import ProductRating, Review


@receiver(post_save, sender=Review)
def update_product_rating_on_save(sender, instance, **kwargs):
    produt = instance.product
    reviews = produt.reviews.all()
    total_reviews = reviews.count()

    reviews_average = reviews.aggregate(Avg("rating"))["rating__avg"] or 0.0

    product_rating, created = ProductRating.objects.get_or_create(product=produt)
    product_rating.average_rating = reviews_average
    product_rating.total_reviews = total_reviews
    product_rating.save()


@receiver(post_delete, sender=Review)
def update_product_rating_on_delete(sende, instance, **kwargs):
    product = instance.product
    reviews = product.reviews.all()
    total_reviews = reviews.conunt()

    reviews_average = reviews.aggregate(Avg("rating"))["rating__avg"] or 0.0

    product_rating, created = ProductRating.objects.get_or_create(product=product)
    product_rating.average_rating = reviews_average
    product_rating.total_reviews = reviews_average
    product_rating.save()

