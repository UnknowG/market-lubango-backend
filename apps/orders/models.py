from django.db import models
from django.conf import settings
import uuid


class Order(models.Model):
    """
    Modelo para representar pedidos no sistema.
    """

    ORDER_STATUS_CHOICES = [
        ("pending", "Pendente"),
        ("confirmed", "Confirmado"),
        ("processing", "Em Processamento"),
        ("shipped", "Enviado"),
        ("delivered", "Entregue"),
        ("cancelled", "Cancelado"),
    ]

    PAYMENT_STATUS_CHOICES = [
        ("pending", "Pendente"),
        ("paid", "Pago"),
        ("failed", "Falhou"),
        ("refunded", "Reembolsado"),
    ]

    order_number = models.CharField(max_length=20, unique=True, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="orders"
    )
    status = models.CharField(
        max_length=20, choices=ORDER_STATUS_CHOICES, default="pending"
    )
    payment_status = models.CharField(
        max_length=20, choices=PAYMENT_STATUS_CHOICES, default="pending"
    )
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    shipping_address = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.order_number:
            # Gerar um número único para cada pedido
            self.order_number = f"ORD-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)

    def __str__(self):
        return self.order_number


class OrderItem(models.Model):
    """
    Modelo para representar itens de um pedido.
    """

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey("products.Product", on_delete=models.CASCADE)
    quantity = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return (
            f"{self.quantity} x {self.product.name} pedido: {self.order.order_number}."
        )


class Payment(models.Model):
    """
    Modelo para representar pagamentos de pedidos.
    """

    PAYMENT_METHOD_CHOICES = [
        ("reference", "Pagamento por Referência"),
        ("mobile", "Pagamento Móvel"),
        ("card", "Pagamento com Cartão"),
    ]

    PAYMENT_STATUS_CHOICES = [
        ("pending", "Pendente"),
        ("processing", "Em Processamento"),
        ("completed", "Concluído"),
        ("failed", "Falhou"),
        ("refunded", "Reembolsado"),
    ]

    order = models.OneToOneField(
        Order, on_delete=models.CASCADE, related_name="payment"
    )
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    payment_status = models.CharField(
        max_length=20, choices=PAYMENT_STATUS_CHOICES, default="pending"
    )
    transaction_id = models.CharField(max_length=100, blank=True, null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    reference_number = models.CharField(max_length=50, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Pagamento para o pedido: {self.order.order_number}"
