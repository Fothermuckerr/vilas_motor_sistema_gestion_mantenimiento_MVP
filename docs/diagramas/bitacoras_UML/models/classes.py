class Rol:
    def __init__(self, id_rol: int, nombre: str, descripcion: str):
        self.id_rol = id_rol
        self.nombre = nombre
        self.descripcion = descripcion

    # def tienePermiso(self, accion: str) -> bool:
    #     pass ///Django: @authenticated


class Cliente:
    def __init__(self, id_cliente:int, rut:str, razon_social:str, email_contacto:str, telefono:str, activo:bool, creado_en):
        self.id_cliente = id_cliente
        self.rut = rut
        self.razon_social = razon_social
        self.email_contacto = email_contacto
        self.telefono = telefono
        self.activo = activo
        self.creado_en = creado_en

class Usuario:
    def __init__(self, id_usuario:int, id_rol:int, id_cliente:int, nombre:str, email:str, password_hash:str, activo:bool, ultimo_acceso, creado_en):
        self.id_usuario = id_usuario
        self.id_rol = id_rol
        self.id_cliente = id_cliente
        self.nombre = nombre
        self.email = email
        self.password_hash = password_hash
        self.activo = activo
        self.ultimo_acceso = ultimo_acceso
        self.creado_en = creado_en

    #def autenticar(self, clave:str) -> bool:
        #pass #Django: authenticate(request, username=email, password=clave)

    #def cambiarClave(self, nueva:str) -> None:
        #pass #Django: user.set_password(nueva); user.save()

    #def desactivar(self) -> None:
        #pass #Django: user.is_active = False; user.save()

class TipoEquipo:
    def __init__(self, id_tipo_equipo: int, nombre:str, unidad_medida:str):
        self.id_tipo_equipo = id_tipo_equipo
        self.nombre = nombre
        self.unidad_medida = unidad_medida

    def obtenerPlan(self) -> 'PlanMantencion':
        pass

class Equipo:
    def __init__(self, id_equipo: int, id_tipo_equipo: int, codigo: str, patente: str, marca: str, modelo: str, numero_serie: str, estado: str, horometro_actual: float, telemetria_id: str):
        self.id_equipo = id_equipo
        self.id_tipo_equipo = id_tipo_equipo
        self.codigo = codigo
        self.patente = patente
        self.marca = marca
        self.modelo = modelo
        self.numero_serie = numero_serie
        self.estado = estado
        self.horometro_actual = horometro_actual
        self.telemetria_id = telemetria_id

    def cambiarEstado(self, estado:str) -> None:
        self.estado = estado
        self.save()
        #Nota: la clase entera debe heredar de models.Models en django para que funcione.

    def actualizarHorometro(self, valor: float) -> None:
        self.horometro_actual = valor
        self.save() #¿deberia poner un return?

    def ultimaLectura(self) -> 'LecturaHorometro':
        self.lecturahorometro_set.lastest('fecha_hora')

class PlanMantecion:
    def __init__(self, id_plan:int, id_tipo_equipo:int, nombre:str):
        self.id_plan = id_plan
        self.id_tipo_equipo = id_tipo_equipo
        self.nombre = nombre

    def serviciosOrdenados(self) -> list:
        pass
        #self.servicio_set.order_by('intervalo_horas')

class ServicioPlan:
    def __init__(self, id_servicio_plan: int, id_plan: int, nombre: str,
                 intervalo_horas: int, descripcion: str):
        self.id_servicio_plan = id_servicio_plan
        self.id_plan = id_plan
        self.nombre = nombre
        self.intervalo_horas = intervalo_horas
        self.descripcion = descripcion

    def insumosRequeridos(self) -> list:
        pass  # self.servicioplaninsumo_set.all()

class Insumo:
    def __init__(self, id_insumo: int, codigo: str, nombre: str, unidad_medida: str):
        self.id_insumo = id_insumo
        self.codigo = codigo
        self.nombre = nombre
        self.unidad_medida = unidad_medida

    # def hayStock(self, cantidad: float) -> bool:
    #     pass  # Fuera de alcance: el sistema no gestiona inventario

    # def descontarStock(self, cantidad: float) -> None:
    #     pass  # Fuera de alcance: el sistema no gestiona inventario

class ServicioPlanInsumo:
    def __init__(self, id_servicio_plan: int, id_insumo: int, cantidad: float):
        self.id_servicio_plan = id_servicio_plan
        self.id_insumo = id_insumo
        self.cantidad = cantidad

class Arriendo:
    def __init__(self, id_arriendo: int, id_equipo: int, id_cliente: int,
                 fecha_inicio, fecha_termino):
        self.id_arriendo = id_arriendo
        self.id_equipo = id_equipo
        self.id_cliente = id_cliente
        self.fecha_inicio = fecha_inicio
        self.fecha_termino = fecha_termino

    def cerrar(self, fecha_termino) -> None:
        pass  # self.fecha_termino = fecha_termino; self.save()

    def estaVigente(self) -> bool:
        pass  # return self.fecha_termino is None or self.fecha_termino >= date.today()


class LecturaHorometro:
    def __init__(self, id_lectura: int, id_equipo: int, id_usuario: int,
                 valor: float, fecha_hora, fuente: str, validada: bool,
                 observacion: str):
        self.id_lectura = id_lectura
        self.id_equipo = id_equipo
        self.id_usuario = id_usuario
        self.valor = valor
        self.fecha_hora = fecha_hora
        self.fuente = fuente
        self.validada = validada
        self.observacion = observacion

    # def guardar(self) -> None:
    #     pass  # Django: self.save()

    # def marcarValidada(self) -> None:
    #     pass  # self.validada = True; self.save()

class SolicitudHorometro:
    def __init__(self, id_solicitud: int, id_equipo: int, id_cliente: int,
                 id_usuario_solicita: int, fecha_solicitud, estado: str,
                 id_lectura: int):
        self.id_solicitud = id_solicitud
        self.id_equipo = id_equipo
        self.id_cliente = id_cliente
        self.id_usuario_solicita = id_usuario_solicita
        self.fecha_solicitud = fecha_solicitud
        self.estado = estado
        self.id_lectura = id_lectura

    def cumplir(self, lectura) -> None:
        pass  # self.estado = 'CUMPLIDA'; self.id_lectura = lectura.id_lectura; self.save()

    def marcarVencida(self) -> None:
        pass  # self.estado = 'VENCIDA'; self.save()

class OrdenTrabajo:
    def __init__(self, id_ot: int, id_equipo: int, id_servicio_plan: int, tipo: str, estado: str, numero_ot: str,
                 fecha_programada, fecha_ejecucion, horometro_cierre: float,
                 observaciones: str):
        self.id_ot = id_ot
        self.id_equipo = id_equipo
        self.id_servicio_plan = id_servicio_plan
        self.tipo = tipo
        self.estado = estado
        self.numero_ot = numero_ot
        self.fecha_programada = fecha_programada
        self.fecha_ejecucion = fecha_ejecucion
        self.horometro_cierre = horometro_cierre
        self.observaciones = observaciones

    def programar(self, fecha) -> None:
        pass  # self.fecha_programada = fecha; self.save()

    def registrarInsumo(self, insumo, cantidad: float) -> None:
        pass  # OrdenTrabajoInsumo.objects.create(...)

    def cerrar(self, horometro: float) -> None:
        pass  # self.estado = 'CERRADA'; self.horometro_cierre = horometro; self.save()


class OrdenTrabajoInsumo:
    def __init__(self, id_ot: int, id_insumo: int, cantidad_usada: float,
                 notas: str):
        self.id_ot = id_ot
        self.id_insumo = id_insumo
        self.cantidad_usada = cantidad_usada
        self.notas = notas


class Auditoria:
    def __init__(self, id_auditoria: int, id_usuario: int, fecha_hora,
                 entidad: str, id_registro: int, operacion: str,
                 valor_anterior, valor_nuevo, ip: str):
        self.id_auditoria = id_auditoria
        self.id_usuario = id_usuario
        self.fecha_hora = fecha_hora
        self.entidad = entidad
        self.id_registro = id_registro
        self.operacion = operacion
        self.valor_anterior = valor_anterior
        self.valor_nuevo = valor_nuevo
        self.ip = ip

    # def registrar(self, entidad: str, id: int, operacion: str,
    #               antes, despues) -> None:
    #     pass  # Se puede implementar con signals de Django o middleware

class ArchivoAdjunto:
    def __init__(self, id_archivo: int, id_usuario_subio: int, entidad: str,
                 id_registro: int, nombre_original: str, ruta: str,
                 mime: str, subido_en):
        self.id_archivo = id_archivo
        self.id_usuario_subio = id_usuario_subio
        self.entidad = entidad
        self.id_registro = id_registro
        self.nombre_original = nombre_original
        self.ruta = ruta
        self.mime = mime
        self.subido_en = subido_en

    # def guardar(self, archivo) -> str:
    #     pass  # Django: self.save(); el archivo se maneja con FileField


class Notificacion:
    """
    NOTA: No se usa en el backend según diseño.
    Se conserva en el esquema solo como elemento de escalabilidad.
    """
    def __init__(self, id_notificacion: int, id_usuario_destino: int,
                 id_equipo: int, tipo: str, contenido, estado: str,
                 enviada_en):
        self.id_notificacion = id_notificacion
        self.id_usuario_destino = id_usuario_destino
        self.id_equipo = id_equipo
        self.tipo = tipo
        self.contenido = contenido
        self.estado = estado
        self.enviada_en = enviada_en

    # def enviar(self) -> None:
    #     pass  # No se usa en MVP

    # def marcarError(self) -> None:
    #     pass  # No se usa en MVP


class TelemetriaEquipo:
    def __init__(self, id_telemetria: int, id_equipo: int, ts,
                 horometro: float, payload):
        self.id_telemetria = id_telemetria
        self.id_equipo = id_equipo
        self.ts = ts
        self.horometro = horometro
        self.payload = payload

    # def importar(self, payload) -> None:
    #     pass  # Fuera del alcance del MVP (sin acceso a telemetría)


# ============================================================
# CLASES DE LÓGICA PURA (NO SON TABLAS SQL)
# Provienen del UML y se mantienen como servicios.
# ============================================================

class ValidadorDatos:
    def validar(self, equipo, valor) -> bool:
        pass  # Servicio de validación, no modelo


class CalculadoraProximoServicio:
    def __init__(self, umbral_alerta_horas: int):
        self.umbral_alerta_horas = umbral_alerta_horas

    def calcularProximoServicio(self, equipo):
        pass  # Servicio de cálculo, no modelo

    def horasRestantes(self, equipo) -> float:
        pass  # Servicio de cálculo, no modelo