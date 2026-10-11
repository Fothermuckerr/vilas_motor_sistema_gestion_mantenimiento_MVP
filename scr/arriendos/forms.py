from django import forms

from .models import Arriendo


class ArriendoForm(forms.ModelForm):
    class Meta:
        model = Arriendo
        fields = ['equipo', 'cliente', 'fecha_inicio']
        widgets = {
            'fecha_inicio': forms.DateInput(attrs={'type': 'date'}),
        }


class CerrarArriendoForm(forms.Form):
    fecha_termino = forms.DateField(
        label='Fecha de término',
        widget=forms.DateInput(attrs={'type': 'date'}),
    )
