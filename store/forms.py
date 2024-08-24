from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'password1', 'password2', 'email']  # Ajoutez d'autres champs si nécessaires
class ClientUpdateForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'last_name', 'email']  # Supposant que "post-nom" est 'last_name'