from django import forms

from .models import OrdenTrabajo, OrdenTrabajoInsumo, PlanMantencion, ServicioPlan


class OrdenTrabajoForm(forms.ModelForm):
    class Meta:
        model = OrdenTrabajo
        fields = ['equipo', 'servicio_plan', 'tipo', 'fecha_programada', 'observaciones']
        widgets = {
            'fecha_programada': forms.DateInput(attrs={'type': 'date'}),
        }


class OrdenTrabajoInsumoForm(forms.ModelForm):
    class Meta:
        model = OrdenTrabajoInsumo
        fields = ['insumo', 'cantidad_usada', 'notas']


class CerrarOrdenForm(forms.Form):
    horometro_cierre = forms.DecimalField(
        label='Horómetro de cierre',
        max_digits=10,
        decimal_places=1,
    )


class PlanMantencionForm(forms.ModelForm):
    class Meta:
        model = PlanMantencion
        fields = ['tipo_equipo', 'nombre']


class ServicioPlanForm(forms.ModelForm):
    class Meta:
        model = ServicioPlan
        fields = ['plan', 'nombre', 'intervalo_horas', 'descripcion']
