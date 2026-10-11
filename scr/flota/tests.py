from decimal import Decimal

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from arriendos.models import Arriendo
from cuentas.models import Cliente, Rol, Usuario
from flota.models import Equipo, TipoEquipo
from horometros.models import LecturaHorometro


class EquipoTest(TestCase):
    def setUp(self):
        self.tipo = TipoEquipo.objects.create(
            nombre='Generador', unidad_medida=TipoEquipo.UnidadMedida.HORAS
        )
        self.equipo = Equipo.objects.create(tipo_equipo=self.tipo, codigo='EQ-001')

    def test_cambiar_estado(self):
        self.equipo.cambiarEstado(Equipo.Estado.EN_FAENA)
        self.equipo.refresh_from_db()
        self.assertEqual(self.equipo.estado, Equipo.Estado.EN_FAENA)

    def test_cambiar_estado_invalido(self):
        with self.assertRaises(ValueError):
            self.equipo.cambiarEstado('ROTO')

    def test_actualizar_horometro(self):
        self.equipo.actualizarHorometro(Decimal('250.0'))
        self.equipo.refresh_from_db()
        self.assertEqual(self.equipo.horometro_actual, Decimal('250.0'))

    def test_ultima_lectura(self):
        rol, _ = Rol.objects.get_or_create(nombre='planificador', defaults={'descripcion': 'Planificador del sistema de gestión de mantenimiento'})
        usuario = Usuario.objects.create_user(
            email='plan@vilas.cl', password='test1234', nombre='Planificador'
        )
        LecturaHorometro.objects.create(
            equipo=self.equipo, usuario=usuario, valor=Decimal('100.0'),
            fecha_hora=timezone.now(), fuente=LecturaHorometro.Fuente.CLIENTE,
        )
        LecturaHorometro.objects.create(
            equipo=self.equipo, usuario=usuario, valor=Decimal('150.0'),
            fecha_hora=timezone.now(), fuente=LecturaHorometro.Fuente.CLIENTE,
        )
        self.assertEqual(self.equipo.ultimaLectura().valor, Decimal('150.0'))


class MarcarDisponibleTest(TestCase):
    """La vista solo devuelve el equipo a disponible cuando su arriendo terminó."""

    def setUp(self):
        self.rol, _ = Rol.objects.get_or_create(nombre='planificador', defaults={'descripcion': 'Planificador del sistema de gestión de mantenimiento'})
        self.usuario = Usuario.objects.create_user(email='plan@vilas.cl', password='test1234', nombre='Planificador')
        self.tipo = TipoEquipo.objects.create(nombre='Generador', unidad_medida=TipoEquipo.UnidadMedida.HORAS)
        self.equipo = Equipo.objects.create(tipo_equipo=self.tipo, codigo='EQ-001')
        self.cliente = Cliente.objects.create(rut='11111111-1', razon_social='Cliente X')
        self.client.force_login(self.usuario)

    def test_marcar_disponible(self):
        self.equipo.cambiarEstado(Equipo.Estado.EN_FAENA)
        response = self.client.post(reverse('flota:marcar_disponible', args=[self.equipo.id]))
        self.assertRedirects(response, reverse('arriendos:arriendos'))
        self.equipo.refresh_from_db()
        self.assertEqual(self.equipo.estado, Equipo.Estado.DISPONIBLE)

    def test_no_cambia_si_el_arriendo_sigue_vigente(self):
        Arriendo.objects.create(
            equipo=self.equipo, cliente=self.cliente, fecha_inicio=timezone.localdate()
        )
        self.equipo.cambiarEstado(Equipo.Estado.EN_FAENA)
        self.client.post(reverse('flota:marcar_disponible', args=[self.equipo.id]))
        self.equipo.refresh_from_db()
        self.assertEqual(self.equipo.estado, Equipo.Estado.EN_FAENA)


class FlotaViewsTest(TestCase):
    def setUp(self):
        self.rol, _ = Rol.objects.get_or_create(nombre='planificador', defaults={'descripcion': 'Planificador del sistema de gestión de mantenimiento'})
        self.usuario = Usuario.objects.create_user(email='plan@vilas.cl', password='test1234', nombre='Planificador')
        self.tipo = TipoEquipo.objects.create(nombre='Generador', unidad_medida=TipoEquipo.UnidadMedida.HORAS)
        self.equipo = Equipo.objects.create(tipo_equipo=self.tipo, codigo='EQ-001')
        self.client.force_login(self.usuario)

    def test_detalle_equipo(self):
        response = self.client.get(reverse('flota:detalle_equipo', args=[self.equipo.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'EQ-001')
        self.assertContains(response, 'Crear OT')
        self.assertContains(response, 'Crear arriendo')

    def test_detalle_enlaza_con_la_fuente_que_corresponde_al_estado(self):
        """El enlace llega con la fuente ya elegida: el estado dice a quién pedirle."""
        response = self.client.get(reverse('flota:detalle_equipo', args=[self.equipo.id]))
        self.assertContains(response, 'Solicitar horómetro')
        self.assertContains(response, '?fuente=TECNICO')

        self.equipo.cambiarEstado(Equipo.Estado.EN_FAENA)
        response = self.client.get(reverse('flota:detalle_equipo', args=[self.equipo.id]))
        self.assertContains(response, '?fuente=CLIENTE')

        self.equipo.cambiarEstado(Equipo.Estado.EN_MANTENIMIENTO)
        response = self.client.get(reverse('flota:detalle_equipo', args=[self.equipo.id]))
        self.assertContains(response, '?fuente=TELEMETRIA')

    def test_detalle_no_ofrece_arrendar_un_equipo_que_no_esta_disponible(self):
        self.equipo.cambiarEstado(Equipo.Estado.EN_FAENA)
        response = self.client.get(reverse('flota:detalle_equipo', args=[self.equipo.id]))
        self.assertNotContains(response, 'Crear arriendo')

    def test_preseleccion_equipo_en_crear_solicitud(self):
        response = self.client.get(
            reverse('horometros:crear_solicitud'),
            {'fuente': 'TECNICO', 'equipo': self.equipo.id},
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, f'value="{self.equipo.id}" selected')

    def test_crear_tipo_equipo(self):
        response = self.client.post(reverse('flota:crear_tipo_equipo'), {
            'nombre': 'Excavadora',
            'unidad_medida': TipoEquipo.UnidadMedida.HORAS,
        })
        self.assertRedirects(response, reverse('flota:tipos_equipo'))
        self.assertTrue(TipoEquipo.objects.filter(nombre='Excavadora').exists())

    def test_crear_equipo(self):
        response = self.client.post(reverse('flota:crear_equipo'), {
            'codigo': 'EQ-002',
            'tipo_equipo': self.tipo.id,
            'patente': '',
            'marca': '',
            'modelo': '',
            'numero_serie': '',
            'estado': Equipo.Estado.DISPONIBLE,
            'horometro_actual': '0.0',
        })
        self.assertRedirects(response, reverse('flota:equipos'))
        self.assertTrue(Equipo.objects.filter(codigo='EQ-002').exists())
