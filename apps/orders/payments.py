from django.conf import settings
import random
import string
from .models import Order, Payment


# Simulação de sistema de pagamento para AOA-Kwanza
class AOAPaymentProcessor:
    """
    Simula um processador de pagamentos para Kwanza (AOA)
    """

    @staticmethod
    def generate_reference():
        """Gera um número de referência para pagamento."""
        return f"REF-{"".join(random.choices(string.digits, k=12))}"

    @staticmethod
    def process_payment(order: Order, payment_method, reference_number=None):
        """
        Processa o pagamento de um pedido

        Args:
            order: Objeto Order
            payment_method: Método de pagamento ("reference", "mobile", "card")
            reference_number: Número de referência (para pagamentos por referência)

        Returns:
            tuple: (success: bool, transaction_id: str, message: str)
        """

        # Criar registro de pagamento
        payment = Payment.objects.create(
            order=order,
            payment_method=payment_method,
            amount=order.total_amount,
            reference_number=reference_number,
        )

        # Simulação de processamento de pagamento
        # Em um ambiente real, aqui seria feita a integração com o gateway de pagamento
        if getattr(settings, 'TESTING', False):
            # Modo de teste: sempre sucesso
            success = True
        else:
            # Modo normal: 75% de chance de sucesso
            success = random.choice([True, True, True, False])

        if success:
            # Gerar ID de transação
            transaction_id = f"TXN-{"".join(random.choices(string.ascii_uppercase + string.digits, k=16))}"
            payment.transaction_id = transaction_id
            payment.payment_status = "completed"
            payment.save()

            # Atualizar status do pedido
            order.payment_status = "paid"
            order.status = "confirmed"
            order.save()

            return True, transaction_id, "Pagamento processado com sucesso"
        else:
            payment.payment_status = "failed"
            payment.save()

            # Atualizar status do pedido
            order.payment_status = "failed"
            order.save()

            return (
                False,
                None,
                "Pagamento falhou. Por favor, tente novamente ou use outro método.",
            )

    @staticmethod
    def refund_payment(order: Order):
        """
        Processa um reembolso

        Args:
            order: Objeto Order

        Returns:
            tuple: (success: bool, message: str)
        """

        try:
            payment = order.payment

            # Simulação de processamento de reembolso
            if getattr(settings, 'TESTING', False):
                # Modo de teste: sempre sucesso
                success = True
            else:
                # Modo normal: 66% de chance de sucesso
                success = random.choice([True, True, False])

            if success:
                # Gerar ID de transação de reembolso
                refund_id = f"REF-{"".join(random.choices(string.ascii_uppercase + string.digits, k=16))}"
                payment.payment_status = "refunded"
                payment.save()

                # Atualizar status do pedido
                order.payment_status = "refunded"
                order.status = "cancelled"
                order.save()

                return (
                    True,
                    f"Reembolso feito com sucesso. ID do reembolso: {refund_id}",
                )

            else:
                return (
                    False,
                    "Falha no reembolso. Por favor, contacte nosso suporte.",
                )

        except Payment.DoesNotExist:
            return False, "Nenhum pagamento encontrado para este pedido."
