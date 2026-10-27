from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

from .models import Cliente, Usuario


class LoginForm(AuthenticationForm):
    username = forms.EmailField(label='Email', widget=forms.EmailInput(attrs={'autofocus': True}))
    password = forms.CharField(label='Contraseña', strip=False, widget=forms.PasswordInput)


class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = ['rut', 'razon_social', 'email_contacto', 'telefono', 'activo']


class UsuarioForm(UserCreationForm):
    """Alta de usuarios desde el sistema, con contraseñas hasheadas por Django."""

    class Meta(UserCreationForm.Meta):
        model = Usuario
        fields = ['nombre', 'email', 'rol', 'cliente', 'is_active']
        widgets = {
            'email': forms.EmailInput(attrs={'autocomplete': 'email'}),
            'nombre': forms.TextInput(attrs={'autocomplete': 'name'}),
        }
