import random
import string
from django.utils import timezone
from django.db import models
from django.urls import reverse
from django.contrib.auth.models import AbstractUser

from martyrsShop import settings
# from martyrsShop.settings import AUTH_USER_MODEL

# Create your models here.
class Category(models.Model):
    name = models.CharField(max_length=255, null=True)

    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=128)
    slug = models.SlugField(max_length=128)
    price = models.FloatField(default=0.0)
    stock = models.IntegerField(default=0)
    description = models.TextField(blank=True)
    photos = models.ImageField(upload_to="produits", blank=True , null=True)
    category = models.ManyToManyField(Category)
    


    def __str__(self):
       return f"{self.name} ({self.stock})"

class Order(models.Model):
    user=models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    ordered=models.BooleanField(default=False)
    ordered_date = models.DateTimeField(blank=True, null=True)

    def __str__(self):
       return f"{self.user.username} marchandise: {self.product.name} ({self.quantity})"
    class Meta:
        ordering = ['-ordered_date']
    
class Cart(models.Model):
    user=models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    orders = models.ManyToManyField(Order)
   

    def __str__(self):
       return self.user.username
    
    def delete(self,*args, **kwargs):
        for order in self.orders.all():
            order.ordered = True
            order.ordered_date = timezone.now()
            order.save()
        self.orders.clear()
        super().delete(*args, **kwargs)

class diaspo(models.Model):
    image=models.ImageField(upload_to="produits", blank=True , null=True)
    nomImg=models.CharField(max_length=128, null=True)
    detailImg=models.CharField(max_length=128, null=True)

class ArchiveCommande(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    items = models.TextField()
    address = models.CharField(max_length=255)
    commune= models.CharField(max_length=100)
    zip_code = models.CharField(max_length=10)
    total =  models.FloatField(default=0.0)
    date_commande = models.DateTimeField(auto_now_add=True)
    num_tel=models.CharField(max_length=128)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    

class Commande(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    items = models.TextField()  # Ce champ stockera les noms des produits et leurs quantités
    address = models.CharField(max_length=255)
    commune = models.CharField(max_length=100, blank=True, editable=False)
    zip_code = models.CharField(max_length=10)
    total =  models.FloatField(default=0.0)
    date_commande = models.DateTimeField(auto_now_add=True, blank=True,null=False)
    num_tel=models.CharField(max_length=128)
    latitude=models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)

    class Meta:
        ordering = ['-date_commande']
    def generate_zip_code(self):
        return ''.join(random.choices(string.digits, k=5))
    def save(self, *args, **kwargs):
        if not self.zip_code:
            self.zip_code=self.generate_zip_code()
        super().save(*args, **kwargs)
    

class CustomUser(AbstractUser):
    # Ajoutez des champs supplémentaires si nécessaire
    is_livreur = models.BooleanField(default=False)  # Pour identifier si l'utilisateur est un livreur

    def __str__(self):
        return self.username

    

    

