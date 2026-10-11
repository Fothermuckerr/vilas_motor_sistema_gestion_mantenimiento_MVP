from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.utils import timezone

from .forms import LecturaHorometroForm, SolicitudHorometroForm
from .models import LecturaHorometro, SolicitudHorometro
from .services import ValidadorDatos


def lista_solicitudes(request):
    """Peticiones de reporte de horómetro enviadas a los clientes."""
    solicitudes = SolicitudHorometro.objects.select_related('equipo', 'cliente').order_by('-fecha_solicitud')
    return render(request, 'horometros/solicitudes.html', {'solicitudes': solicitudes})


def lista_lecturas(request):
    """Historial de lecturas de horómetro reportadas."""
    lecturas = LecturaHorometro.objects.select_related('equipo').order_by('-fecha_hora')
    return render(request, 'horometros/lecturas.html', {'lecturas': lecturas})


@login_required
def crear_solicitud(request):
    """Crea una solicitud de horómetro hacia un cliente."""
    if request.method == 'POST':
        form = SolicitudHorometroForm(request.POST)
        if form.is_valid():
            solicitud = form.save(commit=False)
            solicitud.usuario_solicita = request.user
            solicitud.fecha_solicitud = timezone.now()
            solicitud.save()
            return redirect('horometros:solicitudes')
    else:
        form = SolicitudHorometroForm(initial={'equipo': request.GET.get('equipo')})
    return render(request, 'horometros/solicitar.html', {'form': form})


@login_required
def registrar_lectura(request):
    """Registra una lectura y actualiza el horómetro del equipo (no retrocede)."""
    if request.method == 'POST':
        form = LecturaHorometroForm(request.POST)
        if form.is_valid():
            lectura = form.save(commit=False)
            validador = ValidadorDatos()
            if not validador.validar(lectura.equipo, lectura.valor):
                form.add_error('valor', 'La lectura no puede ser menor al horómetro actual del equipo.')
            else:
                lectura.usuario = request.user
                lectura.fecha_hora = timezone.now()
                lectura.save()
                lectura.equipo.actualizarHorometro(lectura.valor)
                return redirect('horometros:lecturas')
    else:
        form = LecturaHorometroForm()
    return render(request, 'horometros/registrar.html', {'form': form})
