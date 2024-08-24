# store/signals.py
# store/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import Group

from .models import Commande, CustomUser
from django.db.models.signals import pre_save
from django.contrib.auth.hashers import make_password

@receiver(post_save, sender=CustomUser)
def assign_default_group(sender, instance, created, **kwargs):
    if created:
        if instance.is_livreur:
            livreur_group = Group.objects.get(name='Livreurs')
            instance.groups.add(livreur_group)
        else:
            client_group = Group.objects.get(name='Clients')
            instance.groups.add(client_group)
@receiver(pre_save, sender=CustomUser)
def hash_user_password(sender, instance, **kwargs):
    if instance.pk is None:  # Nouveau utilisateur
        instance.password = make_password(instance.password)
    else:
        # Si l'utilisateur existe déjà, on vérifie si le mot de passe a changé
        existing_user = CustomUser.objects.get(pk=instance.pk)
        if existing_user.password != instance.password:
            instance.password = make_password(instance.password)
