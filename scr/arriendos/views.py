from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .forms import ArriendoForm, CerrarArriendoForm
from .models import Arriendo


def lista_arriendos(request):
    """Contratos de arriendo de equipos a clientes, con su vigencia."""
    arriendos = Arriendo.objects.select_related('equipo', 'cliente').order_by('-fecha_inicio')
    return render(request, 'arriendos/arriendos.html', {'arriendos': arriendos})


def crear_arriendo(request):
    """Asigna un equipo a un cliente. Rechaza equipos con arriendo vigente."""
    if request.method == 'POST':
        form = ArriendoForm(request.POST)
        if form.is_valid():
            equipo = form.cleaned_data['equipo']
            if Arriendo.objects.filter(equipo=equipo, fecha_termino__isnull=True).exists():
                form.add_error('equipo', 'El equipo ya tiene un arriendo vigente.')
            else:
                form.save()
                return redirect('arriendos:arriendos')
    else:
        form = ArriendoForm(initial={'equipo': request.GET.get('equipo')})
    return render(request, 'arriendos/crear.html', {'form': form})


def cerrar_arriendo(request, pk):
    """Cierra un arriendo fijando su fecha de término."""
    arriendo = get_object_or_404(Arriendo, pk=pk)
    if request.method == 'POST':
        form = CerrarArriendoForm(request.POST)
        if form.is_valid():
            arriendo.cerrar(form.cleaned_data['fecha_termino'])
            return redirect('arriendos:arriendos')
    else:
        form = CerrarArriendoForm(initial={'fecha_termino': timezone.localdate()})
    return render(request, 'arriendos/cerrar.html', {'form': form, 'arriendo': arriendo})
