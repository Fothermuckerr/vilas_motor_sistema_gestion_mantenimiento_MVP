from django.urls import path

from . import views

app_name = 'horometros'

urlpatterns = [
    path('solicitudes/', views.lista_solicitudes, name='solicitudes'),
    path('solicitudes/nueva/', views.crear_solicitud, name='crear_solicitud'),
    path('lecturas/', views.lista_lecturas, name='lecturas'),
    path('lecturas/nueva/', views.registrar_lectura, name='registrar_lectura'),
]
