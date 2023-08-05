from django.contrib import admin
from django.urls import path
from .views import *
from .middlewares.auth import auth_middleware

urlpatterns = [
    path('', Index.as_view(), name='homepage'),
    path('store', store, name="store"),
    path('signup', Signup.as_view(), name='signup'),
    path('login', Login.as_view(), name='login'),
    path('logout', logout, name='logout'),
    path('search', search_result, name='search'),
    path('cart', auth_middleware(Cart.as_view()), name='cart'),
    path('orders', OrderView.as_view(), name='order'),
    path('check-out', auth_middleware(Checkout.as_view()), name='checkout'),
]