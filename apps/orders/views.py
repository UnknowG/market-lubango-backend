from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from apps.cart.models import Cart
from .payments import AOAPaymentProcessor
from .models import Order, OrderItem
from .serializers import CreateOrderSerializer, OrderSerializer


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_order(request):
    """
    Criar um novo pedido a partir do carrinho de compras
    """
    serializer = CreateOrderSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    cart_code = serializer.validated_data["cart_code"]
    shipping_address = serializer.validated_data["shipping_address"]
    payment_method = serializer.validated_data["payment_method"]
    reference_number = serializer.validated_data.get("reference_number")

    try:
        # Obter carrinho
        cart = Cart.objects.get(cart_code=cart_code)

        # Verificar se o carrinho tem itens
        if not cart.cartitems.exists():
            return Response(
                {"error": "O carrinho está vazio."}, status=status.HTTP_400_BAD_REQUEST
            )

        # Calcular total
        total_amount = sum(
            item.quantity * item.product.price for item in cart.cartitems.all()
        )

        # Criar pedido
        order = Order.objects.create(
            user=request.user,
            total_amount=total_amount,
            shipping_address=shipping_address,
        )

        # Criar itens do pedido
        for cart_item in cart.cartitems.all():
            # Verificar se o produto ainda está em estoque
            product = cart_item.product
            if not product.in_stock or product.stock_quantity < cart_item.quantity:
                order.delete()
                return Response(
                    {
                        "error": f"O produto {product.name} não tem quantidade suficiente em estoque."
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Criar item do pedido
            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=cart_item.quantity,
                price=product.price,
            )

            # Atualizar estoque
            product.stock_quantity -= cart_item.quantity
            if product.stock_quantity == 0:
                product.in_stock = False
            product.save()

        # Processar pagamento
        success, transaction_id, message = AOAPaymentProcessor.process_payment(
            order, payment_method, reference_number
        )

        if success:
            # Limpar carrinho após pedido bem-sucedido
            cart.cartitems.all().delete()

            # Retornar dados do pedido
            order_serializer = OrderSerializer(order)
            return Response(
                {
                    "order": order_serializer.data,
                    "message": message,
                    "transaction_id": transaction_id,
                },
                status=status.HTTP_201_CREATED,
            )
        else:
            # Se o pagamento falhar, cancelar o pedido
            order.status = "cancelled"
            order.save()

            # Devolver produtos ao estoque
            for item in order.items.all():
                product = item.product
                product.stock_quantity += item.quantity
                product.in_stock = True
                product.save()

            return Response({"error": message}, status=status.HTTP_400_BAD_REQUEST)
    except Cart.DoesNotExist:
        return Response(
            {"error": "Carrinho não encontrado"}, status=status.HTTP_404_NOT_FOUND
        )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_user_orders(request):
    """
    Obtém todos os pedidos do usuário
    """

    orders = Order.objects.filter(user=request.user).order_by("-created_at")
    serializer = OrderSerializer(orders, many=True)
    return Response(serializer.data)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_order_detail(request, order_number):
    """
    Obtém detalhes de um pedido específico
    """

    try:
        order = Order.objects.get(order_number=order_number, user=request.user)
        serializer = OrderSerializer(order)
        return Response(serializer.data)
    except Order.DoesNotExist:
        return Response(
            {"error": "Pedido não encontrado"}, status=status.HTTP_404_NOT_FOUND
        )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def request_refund(request, order_number):
    """
    Solicita reembolso para um pedido
    """

    try:
        order = Order.objects.get(order_number=order_number, user=request.user)

        # Verificar se o pedido é elegível para reembolso
        if order.status not in ["confirmed", "processing", "shipped"]:
            return Response(
                {"error": "Este pedido não é elegível para reembolso"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Processar reembolso
        success, message = AOAPaymentProcessor.refund_payment(order)

        if success:
            return Response({"message": message})
        else:
            return Response({"error": message}, status=status.HTTP_400_BAD_REQUEST)

    except Order.DoesNotExist:
        return Response(
            {"error": "Pedido não encontrado."}, status=status.HTTP_404_NOT_FOUND
        )


# Views para vendedores
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_store_orders(request):
    """
    Obtém todos os pedidos para a loja do vendedor
    """

    # Verificar se o usuário é um vendedor
    if request.user.user_type != "seller":
        return Response(
            {"error": "Apenas vendedores podem acessar os pedidos das lojas."},
            status=status.HTTP_403_FORBIDDEN,
        )

    # Verificar se o vendedor tem uma loja
    if not hasattr(request.user, "store"):
        return Response(
            {"error": "Você não tem uma loja."}, status=status.HTTP_400_BAD_REQUEST
        )

    # Obter itens de pedido para produtos da loja
    store_products = request.user.store.products.values_list("id", flat=True)
    order_items = OrderItem.objects.filter(product_id__in=store_products)

    # Obter pedidos únicos
    order_ids = order_items.values_list("order_id", flat=True).distinct()
    orders = Order.objects.filter(id__in=order_ids).order_by("-created_at")

    serializer = OrderSerializer(orders, many=True)
    return Response(serializer.data)


@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def update_order_status(request, order_number):
    """
    Atualizar o status de um pedido (apenas para vendedores)
    """

    # Verificar se o usuário é um vendedor
    if request.user.user_type != "seller":
        return Response(
            {"error": "Apenas vendedores podem atualizar o status do pedido."},
            status=status.HTTP_403_FORBIDDEN,
        )

    # Verificar se o vendedor tem uma loja
    if not hasattr(request.user, "store"):
        return Response(
            {"error": "Você não tem uma loja."}, status=status.HTTP_400_BAD_REQUEST
        )

    try:
        order = Order.objects.get(order_number=order_number)

        # Verificar se o pedido contém produtos da loja do vendedor
        store_products = request.user.store.products.values_list("id", flat=True)
        has_store_product = order.items.filter(product_id__in=store_products).exists()

        if not has_store_product:
            return Response(
                {"error": "Este pedido não contém produtos da sua loja."},
                status=status.HTTP_403_FORBIDDEN,
            )

        # Obter novo status
        new_status = request.data.get("status")
        if not new_status:
            return Response(
                {"error": "Precisa fornecer um status."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Validar status
        valid_statuses = [choice[0] for choice in Order.ORDER_STATUS_CHOICES]
        if new_status not in valid_statuses:
            return Response(
                {
                    "error": f"Status inválido. Status válidos são: {', '.join(valid_statuses)}"
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Atualizar status
        order.status = new_status
        order.save()

        serializer = OrderSerializer(order)
        return Response(serializer.data)

    except Order.DoesNotExist:
        return Response(
            {"error": "Pedido não encontrado."}, status=status.HTTP_404_NOT_FOUND
        )
