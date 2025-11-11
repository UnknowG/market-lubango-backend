from django.apps import AppConfig


class ReviewsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.reviews"

    def ready(self):
        """
        Importar o signal de criação de reviews para atualizar o rating do produto.
        """
        import apps.reviews.signals
