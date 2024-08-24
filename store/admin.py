from django.contrib import admin

from store.models import ArchiveCommande, Commande, CustomUser, Product,Order,Cart,diaspo,Category
from django.contrib.auth.models import Group
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

CustomUser = get_user_model()

# Register your models here.
admin.site.site_header='MA CUISINE'
admin.site.site_title='Manager of KITCHEN'
admin.site.index_title='Management'
class AdminCommande(admin.ModelAdmin):
    list_display=('user', 'items' , 'address' , 'commune' , 'num_tel' , 'zip_code' , 'total' , 'date_commande' )
    search_fields=('items',)
admin.site.register(Category)
admin.site.register(Product)
admin.site.register(Order)
admin.site.register(Cart)
admin.site.register(diaspo)
admin.site.register(Commande, AdminCommande)
admin.site.register(ArchiveCommande)

class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'is_livreur')
    search_fields = ('username', 'email')

admin.site.register(CustomUser, CustomUserAdmin)

# Supprimer les groupes par défaut et en créer de nouveaux
def create_groups(sender, **kwargs):
    from django.contrib.auth.models import Group
    Group.objects.get_or_create(name='Livreurs')
    Group.objects.get_or_create(name='Clients')

# Exécuter cette fonction lorsque l'application démarre
from django.db.models.signals import post_migrate
post_migrate.connect(create_groups)

