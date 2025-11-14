from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.db.models import Avg, Count
from .models import ProductRating, Review


def update_product_rating(product):
    """
    Função auxiliar para atualizar a classificação de um produto.
    Evita duplicação de código e melhora a manutenção.
    
    Args:
        product: Instância do produto a ser atualizado
    """
    # Usar aggregate para obter ambos os valores em uma única query
    stats = product.reviews.aggregate(
        avg_rating=Avg("rating"),
        total=Count("id")
    )
    
    avg_rating = stats["avg_rating"] or 0.0
    total_reviews = stats["total"]
    
    # Usar update_or_create para evitar race conditions
    ProductRating.objects.update_or_create(
        product=product,
        defaults={
            "average_rating": avg_rating,
            "total_reviews": total_reviews
        }
    )


@receiver(post_save, sender=Review)
def update_product_rating_on_save(sender, instance, **kwargs):
    """
    Atualiza a classificação média de um produto quando uma avaliação é salva.

    Args:
        sender: Modelo que enviou o sinal (Review)
        instance: Instância do modelo que foi salva
    """
    update_product_rating(instance.product)


@receiver(post_delete, sender=Review)
def update_product_rating_on_delete(sender, instance, **kwargs):
    """
    Atualiza a classificação média de um produto quando uma avaliação é excluída.

    Args:
        sender: Modelo que enviou o sinal (Review)
        instance: Instância do modelo que foi excluída
    """
    update_product_rating(instance.product)
