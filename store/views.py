from venv import logger
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
import requests
from martyrsShop import settings
from store.models import Commande, Order, Product,Cart,diaspo
from django.contrib.auth.decorators import login_required 
from django.contrib.auth import login, authenticate, logout,update_session_auth_hash
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm,PasswordChangeForm
from .forms import ClientUpdateForm, CustomUserCreationForm

# Create your views here.
def index(request):
    categories = Category.objects.all()
    produit=diaspo.objects.all()
    paginator=Paginator(categories,1)
    page=request.GET.get('page')
    categories=paginator.get_page(page)
    return render(request, 'store/index.html', context={"categories": categories,"produit":produit})

def product_detail(request,slug):
    product=get_object_or_404(Product, slug=slug)
    return render(request, 'store/detail.html', context={"product": product})

def add_to_cart(request):
    if request.method == 'POST':
        product_id = request.POST.get('product_id')

        try:
            product = Product.objects.get(id=product_id)

            if product.stock < 1:
                return JsonResponse({'error': 'Stock insuffisant'}, status=400)

            cart, created = Cart.objects.get_or_create(user=request.user)
            cart_item, created = Order.objects.get_or_create(
                user=request.user,
                product=product,
                defaults={'quantity': 1}
            )
            if not created:
                cart_item.quantity += 1
                cart_item.save()
            cart.orders.add(cart_item)
            cart.save()
            return JsonResponse({'success':True,'message':'Produit ajouté au panier'})
            # return JsonResponse({'success': 'Produit ajouté au panier'})
        except Product.DoesNotExist:
            return JsonResponse({'error': 'Produit non existant'}, status=404)
    return JsonResponse({'error': 'Requête invalide'}, status=400)
def cart(request):
    if request.method == 'POST':
        order_id=request.POST.get('order_id')
        quantity=request.POST.get('quantity')
        order_item=get_object_or_404(Order, id=order_id)
        order_item.quantity=quantity
        order_item.save()
        return redirect('index')
    cart=get_object_or_404(Cart, user=request.user)

    return render(request, 'store/cart.html', context={"orders": cart.orders.all})
def update_quantity(request):
    if request.method == 'POST'and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        order_id=request.POST.get('order_id')
        quantity=request.POST.get('quantity')
        try:
            quantity=int(quantity)
            if quantity < 1:
                raise ValueError("quantity must be at least 1")
        except ValueError:
            logger.error("Invalid quantity: %s", quantity)
            return JsonResponse({'success':False, 'message':'Invalid quantity'}, status=400)
        try:
            order_item=get_object_or_404(Order, id=order_id)
            order_item.quantity=quantity
            order_item.save()
        except Exception as e:
            logger.error("Error updating order item: %s", e)
            return JsonResponse({'success':False, 'message':'Error updating order item'}, status=500)
        return JsonResponse({'success':True})
    return JsonResponse({'success':False}, status=400)
    

def delete_cart(request):
    if cart := request.user.cart:
        cart.delete()

    return redirect('index')
@login_required
def delete_one_cart(request, product_id):
    item=get_object_or_404(Order,id=product_id, user=request.user)
    item.delete()
    return redirect('cart')
def commande_success(request, order_id):
    order=get_object_or_404(Commande, id=order_id)
    return render(request,'store/commande_success.html', {'order':order})
# def get_coordinates():
#     try:
#         response=requests.get(f'https://ipinfo.io/json?token=238ba9913719bb')
# import requests
# from django.conf import settings

def get_ip_geolocation():
    try:
        url = f'https://ipinfo.io/json?token={settings.IP_GEOLOCATION_API_KEY}'
        print(f"Requesting URL: {url}")
        response = requests.get(url)
        response.raise_for_status()  # Lève une exception pour les codes de statut HTTP d'erreur
        
        # Affiche les informations de débogage
        print(f"Response Status Code: {response.status_code}")
        print(f"Response Content: {response.content.decode('utf-8')}")
        
        data = response.json()
        loc = data.get('loc', '').split(',')
        latitude = loc[0] if len(loc) > 0 else None
        longitude = loc[1] if len(loc) > 1 else None
        return float(latitude) if latitude else None, float(longitude) if longitude else None
    except requests.exceptions.RequestException as e:
        print(f"Error fetching geolocation: {e}")
        return None, None
    except ValueError as e:
        print(f"Error parsing geolocation data: {e}")
        return None, None

def create_commande(request):
    cart = get_object_or_404(Cart, user=request.user)
    orders = cart.orders.all()
    total = sum(order.product.price * order.quantity for order in orders)
    items = ', '.join([f"{order.product.name} à {order.product.price} ({order.quantity})" for order in orders])
       
    if request.method == 'POST':
        user=request.user
        address = request.POST['address']
        country = request.POST['country']
        num_tel = request.POST['num_tel']
        if address and country:
            latitude, longitude = get_ip_geolocation()
            if latitude is None or longitude is None:
                return render(request, 'store/commande.html', {'error':'Impossible de recuperer les coordonnees.'})
        
        commande = Commande(
            user=user,
            address=address,
            commune=country,
            items=items,
            total=total,
            num_tel=num_tel,
            latitude=latitude,
            longitude=longitude   
        )
        commande.save()

        # Vous pouvez vider le panier ici si nécessaire
        Cart.objects.filter(user=user).delete()
        Order.objects.filter(user=user).delete()
        return redirect('commande_success', order_id=commande.id)

    return render(request, 'store/commande.html', {'orders':orders,'items':items, 'total':total })

def search_view(request):
    search_input = request.GET.get('search-input', '')
    if search_input:
        product_object = Product.objects.filter(name__icontains=search_input)
        results = [{'name': product.name,'slug' : product.slug} for product in product_object]
        return JsonResponse({'results': results})
    else:
        return JsonResponse({'results': []})
    
def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('index')
    else:
        form = CustomUserCreationForm()
    return render(request, 'store/register.html', {'form': form})

def deliver_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            if user.is_livreur:
                login(request, user)
                return redirect('livreur_dashboard')
            else:
                form.add_error(None, "Vous n'êtes pas autorisé à vous connecter en tant que livreur.")
    else:
        form = AuthenticationForm()
    return render(request, 'store/deliver_login.html', {'form': form})
def client_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            if not user.is_livreur:  # Vérifie que l'utilisateur n'est pas un livreur
                login(request, user)
                return redirect('index')  # Redirige vers la page d'accueil après la connexion
            else:
                form.add_error(None, "Les livreurs ne peuvent pas se connecter ici.")
    else:
        form = AuthenticationForm()
    return render(request, 'store/client_login.html', {'form': form})

@login_required
def livreur_dashboard(request):
    if not request.user.is_livreur:
        return redirect('index')

    commandes = Commande.objects.all().order_by('-date_commande')

    if request.method == 'POST':
        commande_id = request.POST.get('commande_id')
        zip_code = request.POST.get('zip_code')

        # Récupérer la commande avec l'ID fourni
        commande = get_object_or_404(Commande, id=commande_id)

        # Vérifier si le code ZIP correspond à celui de la commande
        if commande.zip_code == zip_code:
            # Archiver la commande
            ArchiveCommande.objects.create(
                user=commande.user,
                items=commande.items,
                address=commande.address,
                commune=commande.commune,
                zip_code=commande.zip_code,
                total=commande.total,
                num_tel=commande.num_tel,
                date_commande=commande.date_commande,
                latitude=commande.latitude,
                longitude=commande.longitude,
            )
            # Supprimer la commande
            commande.delete()
            return redirect('livreur_dashboard')

        else:
            # Le code ZIP est incorrect
            return render(request, 'store/livreur_dashboard.html', {
                'commandes': commandes,
                'error': 'Code ZIP incorrect pour la commande #' + str(commande_id),
            })

    return render(request, 'store/livreur_dashboard.html', {'commandes': commandes})

    # Assurez-vous que seuls les livreurs accèdent à ce tableau de bord
def logout_view(request):
    logout(request)
    return redirect('index') 
@login_required
def client_update_view(request):
    if request.method == 'POST':
        form = ClientUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('index')  # Redirige vers la page d'accueil après la mise à jour
    else:
        form = ClientUpdateForm(instance=request.user)
    
    return render(request, 'store/client_update.html', {'form': form})
@login_required
def change_password_view(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Pour éviter de déconnecter l'utilisateur après le changement de mot de passe
            return redirect('index')
    else:
        form = PasswordChangeForm(request.user)
    
    return render(request, 'store/change_password.html', {'form': form})
    

from django.shortcuts import render
from django.http import JsonResponse
from django.db.models import Q
from .models import ArchiveCommande, Category, Product
from django.core.paginator import Paginator