from django.urls import path
from .views import (
    product_list,
    product_detail,
    category_list,
    register,
    user_login,
    user_logout,
    create_category,
    create_product,
    create_order,
    contact_view,
    contact_no_csrf_page,
)

urlpatterns = [
    path('', product_list, name='products'),
    path('products/<int:product_id>/', product_detail, name='product_detail'),
    path('categories/', category_list, name='categories'),
    path('register/', register, name='register'),
    path('login/', user_login, name='login'),
    path('logout/', user_logout, name='logout'),
    path('categories/new/', create_category, name='create_category'),
    path('products/new/', create_product, name='create_product'),
    path('products/<int:product_id>/order/', create_order, name='create_order'),
    path('contact/', contact_view, name='contact'),
    path('contact/no-csrf/', contact_no_csrf_page, name='contact_no_csrf'),
]
