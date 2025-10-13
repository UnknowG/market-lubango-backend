from django.urls import path
from . import views


urlpatterns = [
    # Product and Category
    path("products/", views.products_list, name="product_list"),
    path("products/<slug:slug>", views.product_detail, name="product_detail"),
    path("categories/", views.category_list, name="category_list"),
    path("categories/<slug:slug>", views.category_detail, name="category_detail"),
    
    # Seller product management
    path("seller/products/create/", views.create_product, name="create_product"),
    path("seller/products/<slug:slug>", views.manage_product, name="manage_product"),
    
    # Search
    path("search/", views.product_search, name="search"),
    
    # Store products
    path("stores/<slug:slug>/products/", views.store_products, name="store_products"),
]
