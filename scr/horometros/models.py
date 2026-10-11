from django.db import models


class LecturaHorometro(models.Model):
    """Historial de horas reales reportadas por el cliente o el técnico."""

    class Fuente(models.TextChoices):
        """Esto sirve para identificar de donde vino el dato del horometro"""

        CLIENTE = 'CLIENTE', 'Cliente'
        TECNICO = 'TECNICO', 'Técnico'
        PLANIFICACION = 'PLANIFICACION', 'Planificación'
        TELEMETRIA = 'TELEMETRIA', 'Telemetría'

    id = models.BigAutoField(primary_key=True, db_column='id_lectura')
    equipo = models.ForeignKey('flota.Equipo', on_delete=models.PROTECT, db_column='id_equipo', related_name='lecturas')
    usuario = models.ForeignKey('cuentas.Usuario', on_delete=models.PROTECT, db_column='id_usuario', related_name='lecturas')
    valor = models.DecimalField(max_digits=10, decimal_places=1)
    fecha_hora = models.DateTimeField()
    fuente = models.CharField(max_length=15, choices=Fuente.choices)
    validada = models.BooleanField(default=False)
    observacion = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        db_table = 'lectura_horometro'

    def __str__(self):
        return f'{self.equipo} @ {self.valor} ({self.fecha_hora})'


class SolicitudHorometro(models.Model):
    """Petición enviada al cliente para que reporte su horómetro."""

    class Estado(models.TextChoices):
        PENDIENTE = 'PENDIENTE', 'Pendiente'
        CUMPLIDA = 'CUMPLIDA', 'Cumplida'
        VENCIDA = 'VENCIDA', 'Vencida'

    id = models.AutoField(primary_key=True, db_column='id_solicitud')
    equipo = models.ForeignKey('flota.Equipo', on_delete=models.PROTECT, db_column='id_equipo', related_name='solicitudes_horometro')
    cliente = models.ForeignKey('cuentas.Cliente', on_delete=models.PROTECT, db_column='id_cliente', related_name='solicitudes_horometro')
    usuario_solicita = models.ForeignKey('cuentas.Usuario', on_delete=models.PROTECT, db_column='id_usuario_solicita', related_name='solicitudes_realizadas')
    fecha_solicitud = models.DateTimeField()
    estado = models.CharField(max_length=10, choices=Estado.choices, default=Estado.PENDIENTE) #Una solicitud siempre nace como pendiente
    lectura = models.OneToOneField(LecturaHorometro, on_delete=models.PROTECT, db_column='id_lectura', null=True, blank=True, related_name='solicitud')

    class Meta:
        db_table = 'solicitud_horometro'

    def __str__(self):
        return f'{self.equipo} ({self.estado})'

    def cumplir(self, lectura):
        """Marca la solicitud cumplida y la vincula a la lectura reportada."""
        self.estado = self.Estado.CUMPLIDA
        self.lectura = lectura
        self.save(update_fields=['estado', 'lectura'])

    def marcarVencida(self):
        """Marca la solicitud como vencida."""
        self.estado = self.Estado.VENCIDA
        self.save(update_fields=['estado'])
