from django.urls import path
from . import views

urlpatterns = [
    # Core pages
    path('', views.home_view, name='home'),
    path('hotel/<int:hotel_id>/', views.hotel_menu_view, name='hotel_menu'),
    path('about/', views.about_view, name='about'),
    path('contact/', views.contact_view, name='contact'),

    # Authentication
    path('auth/login/', views.login_view, name='login'),
    path('auth/signup/', views.signup_view, name='signup'),
    path('auth/logout/', views.logout_view, name='logout'),
    path('auth/forgot-password/', views.forgot_password_view, name='forgot_password'),

    # Cart operations
    path('cart/', views.cart_detail, name='cart'),
    path('cart/add/', views.add_to_cart, name='add_to_cart'),
    path('cart/update/', views.update_cart_item, name='update_cart_item'),
    path('cart/apply-coupon/', views.apply_coupon, name='apply_coupon'),
    path('cart/remove-coupon/', views.remove_coupon, name='remove_coupon'),

    # Checkout & Payment
    path('checkout/', views.checkout_view, name='checkout'),
    path('payment/', views.payment_view, name='payment'),
    path('payment/success/', views.payment_success_view, name='payment_success'),
    
    # Tracking & History
    path('order/tracking/<int:order_id>/', views.order_tracking_view, name='order_tracking'),
    path('order/reorder/<int:order_id>/', views.reorder, name='reorder'),
    path('profile/', views.profile_view, name='profile'),

    # APIs
    path('api/search/', views.search_api, name='search_api'),
    path('api/favorite/toggle/', views.toggle_favorite, name='toggle_favorite'),
]
