from django.shortcuts import redirect, render

from arriendos.models import Arriendo
from cuentas.forms import ClienteForm
from cuentas.models import Cliente
from flota.models import Equipo
from mantencion.models import OrdenTrabajo
from mantencion.services import CalculadoraProximoServicio

UMBRAL_ALERTA_HORAS = 100


def home(request):
    """Pantalla de inicio: resumen general de la operación."""
    contexto = {
        'total_equipos': Equipo.objects.count(),
        'total_clientes': Cliente.objects.count(),
        'total_arriendos': Arriendo.objects.count(),
        'total_ot': OrdenTrabajo.objects.count(),
    }
    return render(request, 'cuentas/home.html', contexto)


def catalogos(request):
    """Índice de catálogos: acceso a cada listado maestro."""
    return render(request, 'cuentas/catalogos.html')


def lista_clientes(request):
    """Cartera de clientes."""
    clientes = Cliente.objects.order_by('razon_social')
    return render(request, 'cuentas/clientes.html', {'clientes': clientes})


def crear_cliente(request):
    """Crea un cliente en la cartera."""
    if request.method == 'POST':
        form = ClienteForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('cuentas:clientes')
    else:
        form = ClienteForm()
    return render(request, 'cuentas/crear_cliente.html', {'form': form})


def dashboard(request):
    """Panel operativo: estado del próximo servicio de cada equipo."""
    equipos = Equipo.objects.select_related('tipo_equipo').order_by('codigo')
    calculadora = CalculadoraProximoServicio(umbral_alerta_horas=UMBRAL_ALERTA_HORAS)

    filas = []
    for equipo in equipos:
        proximo = calculadora.calcularProximoServicio(equipo)
        horas_restantes = calculadora.horasRestantes(equipo, proximo) if proximo else None
        filas.append({
            'equipo': equipo,
            'proximo': proximo,
            'horas_restantes': horas_restantes,
            'en_alerta': proximo is not None and calculadora.estaEnAlerta(equipo, proximo),
        })

    return render(request, 'cuentas/dashboard.html', {
        'filas': filas,
        'umbral_alerta': UMBRAL_ALERTA_HORAS,
    })
