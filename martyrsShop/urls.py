"""
URL configuration for martyrsShop project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django import views
from django.contrib import admin
from django.urls import path

from martyrsShop.settings import STATIC_URL
from store.views import add_to_cart, cart, change_password_view, client_login, client_update_view, delete_cart, deliver_login, index, livreur_dashboard, logout_view, product_detail, register,update_quantity,delete_one_cart,create_commande,commande_success,search_view
from django.conf.urls.static import static

from martyrsShop import settings

urlpatterns = [
    path('',index, name='index'),
    path('admin/', admin.site.urls),
    path('cart/', cart,name="cart"),
    path('update_quantity/', update_quantity,name="update_quantity"),
    path('delete_one_cart/<int:product_id>', delete_one_cart,name="delete_one_cart"),
    path('cart/delete', delete_cart,name="delete-cart"),
    path('create_commande/', create_commande,name="create_commande"),
    path('Product/<str:slug>', product_detail, name="Product"),
    path('add_to_cart/', add_to_cart, name='add_to_cart'),
    path('commande_success/<int:order_id>/', commande_success,name="commande_success"),
    path('search/', search_view, name='search'),
    path('register/', register, name='register'),
    path('client_login/', client_login, name='client_login'),
    path('deliver_login/', deliver_login, name='deliver_login'),
    path('livreur_dashboard/', livreur_dashboard, name='livreur_dashboard'),
    path('logout/', logout_view, name='logout'),
    path('client/update/', client_update_view, name='client_update'),
    path('client/change-password/', change_password_view, name='change_password'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
