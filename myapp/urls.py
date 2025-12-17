from django.urls import path
from . import views

app_name = 'myapp'

urlpatterns = [
    # Home and Products
    path('', views.home, name='home'),
    path('products/', views.product_list, name='product_list'),
    path('product/<slug:slug>/', views.product_detail, name='product_detail'),
    
    # Authentication
    path('register/', views.register, name='register'),
    path('vendor-register/', views.vendor_register, name='vendor_register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('profile/', views.profile, name='profile'),
    
    # Vendor
    path('vendor/dashboard/', views.vendor_dashboard, name='vendor_dashboard'),
    path('vendor/product/add/', views.product_create, name='product_create'),
    path('vendor/product/<int:pk>/edit/', views.product_edit, name='product_edit'),
    path('vendor/product/<int:pk>/delete/', views.product_delete, name='product_delete'),
    
    # Buyer
    path('buyer/dashboard/', views.buyer_dashboard, name='buyer_dashboard'),
    path('cart/', views.cart_view, name='cart'),
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/update/<int:cart_id>/', views.update_cart, name='update_cart'),
    path('cart/remove/<int:cart_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('orders/', views.order_history, name='order_history'),
    path('orders/<int:order_id>/', views.order_detail, name='order_detail'),
]