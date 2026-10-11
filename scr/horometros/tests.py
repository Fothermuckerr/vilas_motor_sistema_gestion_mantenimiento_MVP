from datetime import date
from decimal import Decimal

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from arriendos.models import Arriendo
from cuentas.models import Cliente, Rol, Usuario
from flota.models import Equipo, TipoEquipo
from horometros.forms import SolicitudHorometroForm
from horometros.models import LecturaHorometro, SolicitudHorometro
from horometros.services import ValidadorDatos


class ValidadorDatosTest(TestCase):
    def setUp(self):
        self.tipo = TipoEquipo.objects.create(
            nombre='Generador', unidad_medida=TipoEquipo.UnidadMedida.HORAS
        )
        self.equipo = Equipo.objects.create(
            tipo_equipo=self.tipo, codigo='EQ-001', horometro_actual=Decimal('100.0')
        )
        self.validador = ValidadorDatos()

    def test_lectura_igual_o_mayor_es_valida(self):
        self.assertTrue(self.validador.validar(self.equipo, Decimal('100.0')))
        self.assertTrue(self.validador.validar(self.equipo, Decimal('120.0')))

    def test_lectura_menor_es_invalida(self):
        self.assertFalse(self.validador.validar(self.equipo, Decimal('99.9')))

    def test_lectura_negativa_es_invalida(self):
        self.assertFalse(self.validador.validar(self.equipo, Decimal('-5.0')))

    def test_valor_no_numerico_es_invalido(self):
        self.assertFalse(self.validador.validar(self.equipo, 'no-numero'))
        self.assertFalse(self.validador.validar(self.equipo, None))


class SolicitudHorometroTest(TestCase):
    def setUp(self):
        self.rol, _ = Rol.objects.get_or_create(nombre='planificador', defaults={'descripcion': 'Planificador del sistema de gestión de mantenimiento'})
        self.usuario = Usuario.objects.create_user(
            email='plan@vilas.cl', password='test1234', nombre='Planificador'
        )
        self.cliente = Cliente.objects.create(rut='11111111-1', razon_social='Cliente X')
        self.tipo = TipoEquipo.objects.create(
            nombre='Generador', unidad_medida=TipoEquipo.UnidadMedida.HORAS
        )
        self.equipo = Equipo.objects.create(tipo_equipo=self.tipo, codigo='EQ-001')
        self.solicitud = SolicitudHorometro.objects.create(
            equipo=self.equipo,
            cliente=self.cliente,
            usuario_solicita=self.usuario,
            fecha_solicitud=timezone.now(),
        )

    def test_cumplir(self):
        lectura = LecturaHorometro.objects.create(
            equipo=self.equipo,
            usuario=self.usuario,
            valor=Decimal('150.0'),
            fecha_hora=timezone.now(),
            fuente=LecturaHorometro.Fuente.CLIENTE,
        )
        self.solicitud.cumplir(lectura)
        self.solicitud.refresh_from_db()
        self.assertEqual(self.solicitud.estado, SolicitudHorometro.Estado.CUMPLIDA)
        self.assertEqual(self.solicitud.lectura, lectura)

    def test_marcar_vencida(self):
        self.solicitud.marcarVencida()
        self.solicitud.refresh_from_db()
        self.assertEqual(self.solicitud.estado, SolicitudHorometro.Estado.VENCIDA)


class SolicitudHorometroFormTest(TestCase):
    """El desplegable de clientes debe ofrecer solo al arrendatario del equipo."""

    def setUp(self):
        self.cliente = Cliente.objects.create(rut='11111111-1', razon_social='Cliente X')
        self.otro_cliente = Cliente.objects.create(rut='22222222-2', razon_social='Cliente Y')
        self.tipo = TipoEquipo.objects.create(
            nombre='Generador', unidad_medida=TipoEquipo.UnidadMedida.HORAS
        )
        self.equipo = Equipo.objects.create(tipo_equipo=self.tipo, codigo='EQ-001')
        self.arriendo = Arriendo.objects.create(
            equipo=self.equipo, cliente=self.cliente, fecha_inicio=date(2026, 1, 5)
        )

    def test_ofrece_solo_al_arrendatario(self):
        form = SolicitudHorometroForm(initial={'equipo': self.equipo.id})
        self.assertEqual(list(form.fields['cliente'].queryset), [self.cliente])

    def test_sin_arriendo_no_ofrece_clientes(self):
        self.arriendo.delete()
        form = SolicitudHorometroForm(initial={'equipo': self.equipo.id})
        self.assertFalse(form.fields['cliente'].queryset.exists())

    def test_arriendo_cerrado_no_cuenta(self):
        self.arriendo.cerrar(date(2026, 6, 30))
        form = SolicitudHorometroForm(initial={'equipo': self.equipo.id})
        self.assertFalse(form.fields['cliente'].queryset.exists())

    def test_sin_equipo_no_ofrece_clientes(self):
        form = SolicitudHorometroForm()
        self.assertFalse(form.fields['cliente'].queryset.exists())


class HorometrosViewsTest(TestCase):
    def setUp(self):
        self.rol, _ = Rol.objects.get_or_create(nombre='planificador', defaults={'descripcion': 'Planificador del sistema de gestión de mantenimiento'})
        self.usuario = Usuario.objects.create_user(email='plan@vilas.cl', password='test1234', nombre='Planificador')
        self.cliente = Cliente.objects.create(rut='11111111-1', razon_social='Cliente X')
        self.otro_cliente = Cliente.objects.create(rut='22222222-2', razon_social='Cliente Y')
        self.tipo = TipoEquipo.objects.create(nombre='Generador', unidad_medida=TipoEquipo.UnidadMedida.HORAS)
        self.equipo = Equipo.objects.create(tipo_equipo=self.tipo, codigo='EQ-001', horometro_actual=Decimal('100.0'))
        self.arriendo = Arriendo.objects.create(
            equipo=self.equipo, cliente=self.cliente, fecha_inicio=date(2026, 1, 5)
        )
        self.client.force_login(self.usuario)

    def test_crear_solicitud(self):
        response = self.client.post(reverse('horometros:crear_solicitud'), {
            'equipo': self.equipo.id,
            'cliente': self.cliente.id,
        })
        self.assertRedirects(response, reverse('horometros:solicitudes'))
        self.assertEqual(SolicitudHorometro.objects.count(), 1)

    def test_crear_solicitud_rechaza_cliente_ajeno(self):
        response = self.client.post(reverse('horometros:crear_solicitud'), {
            'equipo': self.equipo.id,
            'cliente': self.otro_cliente.id,
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(SolicitudHorometro.objects.count(), 0)

    def test_registrar_lectura_valida(self):
        response = self.client.post(reverse('horometros:registrar_lectura'), {
            'equipo': self.equipo.id,
            'valor': '150.0',
            'fuente': LecturaHorometro.Fuente.CLIENTE,
            'observacion': '',
        })
        self.assertRedirects(response, reverse('horometros:lecturas'))
        self.equipo.refresh_from_db()
        self.assertEqual(self.equipo.horometro_actual, Decimal('150.0'))

    def test_registrar_lectura_rechaza_retroceso(self):
        response = self.client.post(reverse('horometros:registrar_lectura'), {
            'equipo': self.equipo.id,
            'valor': '90.0',
            'fuente': LecturaHorometro.Fuente.CLIENTE,
            'observacion': '',
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(LecturaHorometro.objects.count(), 0)
        self.assertContains(response, 'no puede ser menor')
