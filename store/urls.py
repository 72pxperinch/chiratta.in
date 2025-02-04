from django.urls import path
from .views import *

urlpatterns = [
    path('', home_view, name='store'),
    path('about/', about_view, name='about'),
    path('contact/', contact_view, name='contact'),
    path('product/<str:pid>', product_view, name='store-product-detail'),
    path('cart/', cart_view, name='store-cart'),
    path('checkout/', checkout_view, name='store-checkout'),
    path('update_item/', update_item, name='store-update_item'),
    path('save_checkout/', save_checkout, name='store-save_checkout'),
    path('make_payment/', make_payment, name='store-make_payment'),
    path('orders/', orders, name='orders'),
    path('invoice/<str:order_id>', get_invoice, name='store-invoice'),
    path('about/<str:data_name>', policy_view, name='store-tnc'),
]
