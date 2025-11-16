from django.urls import path
from . import views


urlpatterns = [
    # Product and Category
    path("", views.products_list, name="product_list"),
    path("categories/", views.category_list, name="category_list"),
    path("search/", views.product_search, name="search"),
    path("seller/create/", views.create_product, name="create_product"),
    path("categories/<slug:slug>", views.category_detail, name="category_detail"),
    path("stores/<slug:slug>/", views.store_products, name="store_products"),
    path("seller/<slug:slug>", views.manage_product, name="manage_product"),
    path("<slug:slug>", views.product_detail, name="product_detail"),
]
