from django.urls import path
from . import views

urlpatterns = [
    # Cart
    path("cart/<str:cart_code>/", views.get_cart, name="get_cart"),
    path("cart/create/", views.create_cart, name="create_cart"),
    path("cart/user/", views.get_user_cart, name="get_user_cart"),
    path("cart/create-user/", views.create_user_cart, name="create_user_cart"),
    path("cart/merge/", views.merge_carts, name="merge_carts"),
    path("cart/add/", views.add_to_cart, name="add_to_cart"),
    path("cart/update/", views.update_cartitem_quantity, name="update_cartitem_quantity"),
    path("cart/item/<int:pk>/", views.delete_cartitem, name="delete_cartitem"),
]
