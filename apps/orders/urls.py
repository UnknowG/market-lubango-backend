from django.urls import path
from . import views

urlpatterns = [
    # Order management
    path("create/", views.create_order, name="create_order"),
    path("", views.get_user_orders, name="user_orders"),
    path("<str:order_number>/", views.get_order_detail, name="order_detail"),
    path("<str:order_number>/refund/", views.request_refund, name="request_refund"),
    # Seller order management
    path("seller/orders/", views.get_store_orders, name="store_orders"),
    path(
        "seller/<str:order_number>/status/",
        views.update_order_status,
        name="update_order_status",
    ),
]
