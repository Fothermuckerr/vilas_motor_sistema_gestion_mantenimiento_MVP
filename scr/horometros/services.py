from decimal import Decimal, InvalidOperation

from arriendos.models import Arriendo
from flota.models import Equipo

from .models import LecturaHorometro


class ValidadorDatos:
    """Valida datos de entrada del dominio, en particular lecturas de horómetro."""

    def validar(self, equipo, valor) -> bool:
        """True si 'valor' es una lectura de horómetro válida para el equipo.

        Reglas:
        - No puede ser negativa.
        - No puede ser menor al horómetro actual (el horómetro no retrocede).
        """
        try:
            lectura = Decimal(valor)
        except (InvalidOperation, TypeError, ValueError):
            return False
        if lectura < 0:
            return False
        return lectura >= equipo.horometro_actual


def arrendatarioDelEquipo(equipo):
    """Cliente que tiene la máquina, o None si nunca se arrendó.

    Da igual si el contrato sigue vigente o ya se cerró: mientras la máquina esté
    en faena, quien la tiene es el último arrendatario, y a él se le pide el dato.
    """
    ultimo = (
        Arriendo.objects.filter(equipo=equipo)
        .select_related('cliente')
        .order_by('-fecha_inicio', '-id')
        .first()
    )
    return ultimo.cliente if ultimo else None


def fuenteSugerida(equipo):
    """Fuente más probable para pedir el horómetro de un equipo.

    Es solo una sugerencia para el enlace de la ficha: con la máquina en faena lo
    natural es pedírselo al cliente, en bodega al técnico, y si está en taller la
    telemetría es lo único que no depende de alguien presente.
    """
    if equipo.estado == Equipo.Estado.EN_FAENA:
        return LecturaHorometro.Fuente.CLIENTE
    if equipo.estado == Equipo.Estado.DISPONIBLE:
        return LecturaHorometro.Fuente.TECNICO
    return LecturaHorometro.Fuente.TELEMETRIA
