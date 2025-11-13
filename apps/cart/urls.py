from django.urls import path
from . import views

urlpatterns = [
    # Cart
    path("create/", views.create_cart, name="create_cart"),
    path("add/", views.add_to_cart, name="add_to_cart"),
    path("update/", views.update_cartitem_quantity, name="update_cartitem_quantity"),
    path("user/", views.get_user_cart, name="get_user_cart"),
    path("create-user/", views.create_user_cart, name="create_user_cart"),
    path("merge/", views.merge_carts, name="merge_carts"),
    path("item/<int:pk>/", views.delete_cartitem, name="delete_cartitem"),
    path("<str:cart_code>/", views.get_cart, name="get_cart"),
]
