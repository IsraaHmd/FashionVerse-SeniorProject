from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
#from .views import get_product_variants, was for ajax product colors..
app_name = 'shop'

urlpatterns = [
    path('', views.index, name='index'),
    path('aboutus/', views.about, name='aboutus'),
    path('contactus/', views.contact, name='contactus'),
    path('shop/', views.shop, name='shop'),
    path('shop/<int:item_id>/', views.shop_item, name='shop_item'),
    
    # path('product/<int:product_color_id>/variants/', get_product_variants, name='get_product_variants'), was for ajax product colors..
    #cart urls:
    #path('cart/', views.cart, name='cart'), replaces with context processors
    path('cart/add/', views.add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('update-cart-size/<int:item_id>/', views.update_cart_size, name='update_cart_size'),
    path('update_cart_quantity/<int:item_id>/', views.update_cart_quantity, name='update_cart_quantity'),
    # Add this to your urlpatterns in urls.py
    path('search/', views.search_products, name='search_products'),
    #Checkout
    path('checkout/', views.checkout, name='checkout'),
    path('place_order/', views.place_order, name='place_order'),

    #contactus
    path('contactus/', views.contact, name='contactus'),

    #wishlist
    path('wishlist/', views.wishlist_view, name='wishlist'),
    path('wishlist/toggle/', views.toggle_wishlist_item, name='toggle_wishlist'),
]

#The below ensures that when you're in development mode (DEBUG=True), Django will automatically serve media files (e.g., images) stored in your media folder.
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)