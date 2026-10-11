from decimal import Decimal

from .models import OrdenTrabajo, ServicioPlan


class CalculadoraProximoServicio:
    """Calcula cuándo corresponde la próxima mantención de un equipo.

    Regla de negocio: un equipo pertenece a un tipo de equipo, que tiene planes,
    y cada plan tiene servicios con un intervalo de horas. El próximo servicio es
    aquel cuyo vencimiento está más cerca, medido como la diferencia entre el
    horómetro actual del equipo y el horómetro de cierre de su última OT cerrada
    para ese servicio.
    """

    def __init__(self, umbral_alerta_horas):
        self.umbral_alerta_horas = umbral_alerta_horas

    def serviciosDelEquipo(self, equipo):
        """Servicios con intervalo definido para el tipo de equipo."""
        return ServicioPlan.objects.filter(
            plan__tipo_equipo=equipo.tipo_equipo,
            intervalo_horas__isnull=False,
        )

    def ultimoHorometroMantencion(self, equipo, servicio):
        """Horómetro de cierre de la última OT cerrada para un servicio, o 0."""
        ultima = (
            OrdenTrabajo.objects.filter(
                equipo=equipo,
                servicio_plan=servicio,
                estado=OrdenTrabajo.Estado.CERRADA,
                horometro_cierre__isnull=False,
            )
            .order_by('-horometro_cierre')
            .first()
        )
        return ultima.horometro_cierre if ultima else Decimal('0.0')

    def horasRestantes(self, equipo, servicio):
        """Horas que faltan para vencer el intervalo del servicio (negativo si venció)."""
        ultimo = self.ultimoHorometroMantencion(equipo, servicio)
        horas_transcurridas = equipo.horometro_actual - ultimo
        return Decimal(servicio.intervalo_horas) - horas_transcurridas

    def calcularProximoServicio(self, equipo):
        """Devuelve el próximo servicio a realizar, o None si el equipo no tiene servicios."""
        servicios = list(self.serviciosDelEquipo(equipo))
        if not servicios:
            return None
        return min(servicios, key=lambda servicio: self.horasRestantes(equipo, servicio))

    def estaEnAlerta(self, equipo, servicio=None):
        """True si el próximo servicio está dentro del umbral de alerta."""
        proximo = servicio or self.calcularProximoServicio(equipo)
        if proximo is None:
            return False
        return self.horasRestantes(equipo, proximo) <= self.umbral_alerta_horas
