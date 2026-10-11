from django.contrib import admin

from .models import ArchivoAdjunto, Auditoria


@admin.register(Auditoria)
class AuditoriaAdmin(admin.ModelAdmin):
    list_display = ('fecha_hora', 'entidad', 'id_registro', 'operacion', 'usuario', 'ip')
    list_filter = ('operacion', 'entidad')


@admin.register(ArchivoAdjunto)
class ArchivoAdjuntoAdmin(admin.ModelAdmin):
    list_display = ('nombre_original', 'entidad', 'id_registro', 'mime', 'subido_en')
