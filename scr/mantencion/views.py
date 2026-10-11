from django.shortcuts import get_object_or_404, redirect, render

from .forms import (
    CerrarOrdenForm,
    OrdenTrabajoForm,
    OrdenTrabajoInsumoForm,
    PlanMantencionForm,
    ServicioPlanForm,
)
from .models import OrdenTrabajo, PlanMantencion, ServicioPlan


def lista_planes(request):
    """Planes de mantención y sus servicios por tipo de equipo."""
    planes = PlanMantencion.objects.select_related('tipo_equipo').order_by('nombre')
    servicios = ServicioPlan.objects.select_related('plan__tipo_equipo').order_by('intervalo_horas')
    return render(request, 'mantencion/planes.html', {'planes': planes, 'servicios': servicios})


def lista_ordenes_trabajo(request):
    """Órdenes de trabajo programadas y ejecutadas."""
    ordenes = OrdenTrabajo.objects.select_related('equipo', 'servicio_plan').order_by('-id')
    return render(request, 'mantencion/ordenes_trabajo.html', {'ordenes': ordenes})


def crear_plan(request):
    """Crea un plan de mantención para un tipo de equipo."""
    if request.method == 'POST':
        form = PlanMantencionForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('mantencion:planes')
    else:
        form = PlanMantencionForm()
    return render(request, 'mantencion/crear_plan.html', {'form': form})


def crear_servicio(request):
    """Crea un servicio (con su intervalo) dentro de un plan."""
    if request.method == 'POST':
        form = ServicioPlanForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('mantencion:planes')
    else:
        form = ServicioPlanForm()
    return render(request, 'mantencion/crear_servicio.html', {'form': form})


def crear_orden(request):
    """Programa una nueva OT. El número se genera automáticamente (OT-0001...)."""
    if request.method == 'POST':
        form = OrdenTrabajoForm(request.POST)
        if form.is_valid():
            orden = form.save(commit=False)
            orden.numero_ot = 'TEMP'
            orden.save()
            orden.numero_ot = f'OT-{orden.id:04d}'
            orden.save(update_fields=['numero_ot'])
            return redirect('mantencion:detalle_orden', pk=orden.pk)
    else:
        form = OrdenTrabajoForm(initial={'equipo': request.GET.get('equipo')})
    return render(request, 'mantencion/crear_orden.html', {'form': form})


def detalle_orden(request, pk):
    """Ficha de una OT con sus insumos usados."""
    orden = get_object_or_404(
        OrdenTrabajo.objects.select_related('equipo', 'servicio_plan').prefetch_related('insumos__insumo'),
        pk=pk,
    )
    return render(request, 'mantencion/detalle_orden.html', {'orden': orden})


def registrar_insumo(request, pk):
    """Registra un insumo real usado en la OT."""
    orden = get_object_or_404(OrdenTrabajo, pk=pk)
    if request.method == 'POST':
        form = OrdenTrabajoInsumoForm(request.POST)
        if form.is_valid():
            orden.registrarInsumo(
                insumo=form.cleaned_data['insumo'],
                cantidad=form.cleaned_data['cantidad_usada'],
                notas=form.cleaned_data['notas'],
            )
            return redirect('mantencion:detalle_orden', pk=orden.pk)
    else:
        form = OrdenTrabajoInsumoForm()
    return render(request, 'mantencion/registrar_insumo.html', {'form': form, 'orden': orden})


def cerrar_orden(request, pk):
    """Cierra una OT fijando el horómetro de cierre."""
    orden = get_object_or_404(OrdenTrabajo, pk=pk)
    if request.method == 'POST':
        form = CerrarOrdenForm(request.POST)
        if form.is_valid():
            orden.cerrar(form.cleaned_data['horometro_cierre'])
            return redirect('mantencion:detalle_orden', pk=orden.pk)
    else:
        form = CerrarOrdenForm()
    return render(request, 'mantencion/cerrar_orden.html', {'form': form, 'orden': orden})
