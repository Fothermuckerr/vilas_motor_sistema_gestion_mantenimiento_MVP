from django.urls import path

from . import views

app_name = 'mantencion'

urlpatterns = [
    path('planes/', views.lista_planes, name='planes'),
    path('planes/nueva/', views.crear_plan, name='crear_plan'),
    path('planes/servicios/nueva/', views.crear_servicio, name='crear_servicio'),
    path('ordenes-trabajo/', views.lista_ordenes_trabajo, name='ordenes_trabajo'),
    path('ordenes-trabajo/nueva/', views.crear_orden, name='crear_orden'),
    path('ordenes-trabajo/<int:pk>/', views.detalle_orden, name='detalle_orden'),
    path('ordenes-trabajo/<int:pk>/insumo/', views.registrar_insumo, name='registrar_insumo'),
    path('ordenes-trabajo/<int:pk>/cerrar/', views.cerrar_orden, name='cerrar_orden'),
]
