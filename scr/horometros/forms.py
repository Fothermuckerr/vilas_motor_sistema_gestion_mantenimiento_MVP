from django import forms

from cuentas.models import Cliente

from .models import LecturaHorometro, SolicitudHorometro


class SolicitudHorometroForm(forms.ModelForm):
    """Solicitud de horómetro hacia el arrendatario de un equipo.

    El horómetro se le pide a quien tiene la máquina. Por eso el campo 'cliente'
    no ofrece el catálogo completo: se limita al cliente con arriendo vigente del
    equipo seleccionado, y queda vacío si el equipo no está arrendado.

    El filtro se recalcula en cada envío, así que un POST manipulado con un
    cliente ajeno no pasa la validación del propio campo.
    """

    class Meta:
        model = SolicitudHorometro
        fields = ['equipo', 'cliente']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['cliente'].queryset = self._clientes_del_equipo()
        if not self.fields['cliente'].queryset.exists():
            self.fields['cliente'].help_text = (
                'El equipo seleccionado no tiene un arriendo vigente, '
                'así que no hay a quién solicitarle el horómetro.'
            )

    def _equipo_seleccionado(self):
        """Id del equipo elegido, venga del POST o del enlace que abrió el formulario."""
        if self.is_bound:
            return self.data.get('equipo') or None
        return self.initial.get('equipo') or None

    def _clientes_del_equipo(self):
        """Clientes con arriendo abierto del equipo seleccionado."""
        equipo_id = self._equipo_seleccionado()
        if not equipo_id:
            return Cliente.objects.none()
        return Cliente.objects.filter(
            arriendos__equipo_id=equipo_id,
            arriendos__fecha_termino__isnull=True,
        ).distinct()


class LecturaHorometroForm(forms.ModelForm):
    class Meta:
        model = LecturaHorometro
        fields = ['equipo', 'valor', 'fuente', 'observacion']
