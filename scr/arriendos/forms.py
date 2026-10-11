from django import forms

from flota.models import Equipo

from .models import Arriendo


class ArriendoForm(forms.ModelForm):
    """Alta de arriendo.

    El desplegable solo ofrece equipos disponibles, y un equipo está disponible
    únicamente cuando su contrato anterior se cerró y además se marcó su
    regreso. El estado resume los dos pasos, así que no hace falta consultar
    arriendos para decidir qué se puede arrendar.
    """

    class Meta:
        model = Arriendo
        fields = ['equipo', 'cliente', 'fecha_inicio']
        widgets = {
            'fecha_inicio': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        campo = self.fields['equipo']
        campo.queryset = Equipo.objects.filter(estado=Equipo.Estado.DISPONIBLE)
        campo.error_messages = {
            **campo.error_messages,
            'invalid_choice': 'El equipo no está disponible para arrendar.',
        }


class CerrarArriendoForm(forms.Form):
    fecha_termino = forms.DateField(
        label='Fecha de término',
        widget=forms.DateInput(attrs={'type': 'date'}),
    )
