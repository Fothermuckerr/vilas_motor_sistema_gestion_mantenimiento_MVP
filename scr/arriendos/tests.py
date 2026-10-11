from datetime import timedelta

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from arriendos.models import Arriendo
from cuentas.models import Cliente, Rol, Usuario
from flota.models import Equipo, TipoEquipo


class ArriendoTest(TestCase):
    def setUp(self):
        self.tipo = TipoEquipo.objects.create(
            nombre='Generador', unidad_medida=TipoEquipo.UnidadMedida.HORAS
        )
        self.equipo = Equipo.objects.create(tipo_equipo=self.tipo, codigo='EQ-001')
        self.cliente = Cliente.objects.create(rut='11111111-1', razon_social='Cliente X')
        self.arriendo = Arriendo.objects.create(
            equipo=self.equipo, cliente=self.cliente, fecha_inicio=timezone.localdate()
        )

    def test_vigente_cuando_abierto(self):
        self.assertTrue(self.arriendo.estaVigente())

    def test_vigente_cuando_no_ha_vencido(self):
        self.arriendo.cerrar(timezone.localdate() + timedelta(days=10))
        self.arriendo.refresh_from_db()
        self.assertTrue(self.arriendo.estaVigente())

    def test_no_vigente_cuando_vencido(self):
        self.arriendo.cerrar(timezone.localdate() - timedelta(days=1))
        self.arriendo.refresh_from_db()
        self.assertFalse(self.arriendo.estaVigente())


class ArriendosViewsTest(TestCase):
    def setUp(self):
        self.rol, _ = Rol.objects.get_or_create(nombre='planificador', defaults={'descripcion': 'Planificador del sistema de gestión de mantenimiento'})
        self.usuario = Usuario.objects.create_user(email='plan@vilas.cl', password='test1234', nombre='Planificador')
        self.tipo = TipoEquipo.objects.create(nombre='Generador', unidad_medida=TipoEquipo.UnidadMedida.HORAS)
        self.equipo = Equipo.objects.create(tipo_equipo=self.tipo, codigo='EQ-001')
        self.cliente = Cliente.objects.create(rut='11111111-1', razon_social='Cliente X')
        self.client.force_login(self.usuario)

    def test_crear_arriendo(self):
        response = self.client.post(reverse('arriendos:crear_arriendo'), {
            'equipo': self.equipo.id,
            'cliente': self.cliente.id,
            'fecha_inicio': timezone.localdate().isoformat(),
        })
        self.assertRedirects(response, reverse('arriendos:arriendos'))
        self.assertEqual(Arriendo.objects.count(), 1)

    def test_crear_arriendo_rechaza_equipo_vigente(self):
        Arriendo.objects.create(equipo=self.equipo, cliente=self.cliente, fecha_inicio=timezone.localdate())
        response = self.client.post(reverse('arriendos:crear_arriendo'), {
            'equipo': self.equipo.id,
            'cliente': self.cliente.id,
            'fecha_inicio': timezone.localdate().isoformat(),
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Arriendo.objects.count(), 1)
        self.assertContains(response, 'ya tiene un arriendo vigente')

    def test_cerrar_arriendo(self):
        arriendo = Arriendo.objects.create(equipo=self.equipo, cliente=self.cliente, fecha_inicio=timezone.localdate())
        fecha = (timezone.localdate() + timedelta(days=5)).isoformat()
        response = self.client.post(reverse('arriendos:cerrar_arriendo', args=[arriendo.id]), {
            'fecha_termino': fecha,
        })
        self.assertRedirects(response, reverse('arriendos:arriendos'))
        arriendo.refresh_from_db()
        self.assertIsNotNone(arriendo.fecha_termino)
