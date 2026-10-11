from django.shortcuts import get_object_or_404, redirect, render

from .forms import EquipoForm, TipoEquipoForm
from .models import Equipo, TipoEquipo


def lista_equipos(request):
    """Inventario de la flota: listado de equipos con su estado y horómetro."""
    equipos = Equipo.objects.select_related('tipo_equipo').order_by('codigo')
    return render(request, 'flota/equipos.html', {'equipos': equipos})


def lista_tipos_equipo(request):
    """Categorías de equipos y su unidad de medida."""
    tipos = TipoEquipo.objects.order_by('nombre')
    return render(request, 'flota/tipos_equipo.html', {'tipos': tipos})


def crear_tipo_equipo(request):
    """Crea una categoría de equipo."""
    if request.method == 'POST':
        form = TipoEquipoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('flota:tipos_equipo')
    else:
        form = TipoEquipoForm()
    return render(request, 'flota/crear_tipo_equipo.html', {'form': form})


def crear_equipo(request):
    """Crea un equipo en el inventario."""
    if request.method == 'POST':
        form = EquipoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('flota:equipos')
    else:
        form = EquipoForm()
    return render(request, 'flota/crear_equipo.html', {'form': form})


def detalle_equipo(request, pk):
    """Ficha del equipo con su historial de lecturas, OT y arriendos."""
    equipo = get_object_or_404(
        Equipo.objects.select_related('tipo_equipo').prefetch_related(
            'lecturas', 'solicitudes_horometro', 'ordenes_trabajo', 'arriendos__cliente'
        ),
        pk=pk,
    )
    return render(request, 'flota/detalle_equipo.html', {'equipo': equipo})
