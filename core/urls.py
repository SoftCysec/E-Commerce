from django.urls import path
from .views import (
    ProductDetailView,
    add_to_cart,
    HomeView,
    ShopView,
    remove_from_cart,
    CheckoutView,
    CartView,
    contact,
    delete_from_cart,
    PaymentView,
    AddCouponView,
    RequestRefundView,
    )
app_name = 'core'
urlpatterns = [
    path('', HomeView.as_view(), name='HomeView'),
    path('productdetails/<slug>/', ProductDetailView.as_view(), name='productdetails'),
    path('shop/', ShopView.as_view(), name='ShopView'),
    path('cartview/', CartView.as_view(), name='cartview' ),
    path('add_to_cart/<slug>/', add_to_cart, name='add_to_cart'),
    path('add_coupon/', AddCouponView.as_view(), name='add_coupon'),
    path('remove_from_cart/<slug>/', remove_from_cart, name='remove_from_cart'),
    path('delete_from_cart/<slug>/', delete_from_cart, name='delete_from_cart'),
    path('checkout/',CheckoutView.as_view(), name='checkout'),
    path('contact', contact, name='contact'),
    path('payment/<payment_option>/', PaymentView.as_view(), name='payment'),
    path('request-refund/', RequestRefundView.as_view(), name='request-refund'),

]
