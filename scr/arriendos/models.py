from django.db import models
from django.utils import timezone


class Arriendo(models.Model):
    """Contrato de arriendo de un equipo a un cliente."""

    id = models.AutoField(primary_key=True, db_column='id_arriendo')
    equipo = models.ForeignKey('flota.Equipo', on_delete=models.PROTECT, db_column='id_equipo', related_name='arriendos')
    cliente = models.ForeignKey('cuentas.Cliente', on_delete=models.PROTECT, db_column='id_cliente', related_name='arriendos')
    fecha_inicio = models.DateField()
    fecha_termino = models.DateField(null=True, blank=True)

    class Meta:
        db_table = 'arriendo'

    def __str__(self):
        return f'{self.equipo} - {self.cliente}'

    def cerrar(self, fecha_termino):
        """Cierra el arriendo fijando la fecha de término."""
        self.fecha_termino = fecha_termino
        self.save(update_fields=['fecha_termino'])

    def estaVigente(self):
        """True si el arriendo está abierto (sin fecha de término) o aún no vence."""
        if self.fecha_termino is None:
            return True
        return self.fecha_termino >= timezone.localdate()
