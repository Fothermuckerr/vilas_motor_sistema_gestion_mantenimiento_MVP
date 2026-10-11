CREATE DATABASE IF NOT EXISTS vilas_motor CHARACTER SET utf8mb4;
USE vilas_motor;

--TODO: borrar todos los comentarios bajo los comentarios post ; de cada tabla solo los que tienen un "*" al inicio.

-- Creación de tablas en orden de dependencia
CREATE TABLE rol (
    id_rol TINYINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(30) UNIQUE NOT NULL,
    descripcion VARCHAR(120)
);

CREATE TABLE cliente (
    id_cliente INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    rut VARCHAR(12) UNIQUE NOT NULL,
    razon_social VARCHAR(120) NOT NULL,
    email_contacto VARCHAR(120),
    telefono VARCHAR(20),
    activo TINYINT(1) DEFAULT 1,
    creado_en DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE usuario (
    id_usuario INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    id_rol TINYINT UNSIGNED NOT NULL,
    id_cliente INT UNSIGNED,
    nombre VARCHAR(100) NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    activo TINYINT(1) DEFAULT 1,
    ultimo_acceso DATETIME,
    creado_en DATETIME DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_usuario_rol FOREIGN KEY (id_rol) REFERENCES rol(id_rol),
    CONSTRAINT fk_usuario_cliente FOREIGN KEY (id_cliente) REFERENCES cliente(id_cliente)
);

CREATE TABLE tipo_equipo (
    id_tipo_equipo SMALLINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(60) UNIQUE NOT NULL,
    unidad_medida ENUM('HORAS', 'KM') NOT NULL
); -- "Categorías de equipos (ej. Grúa Horquilla, Generador)."

CREATE TABLE equipo (
    id_equipo INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    id_tipo_equipo SMALLINT UNSIGNED NOT NULL,
    codigo VARCHAR(30) UNIQUE NOT NULL,
    patente VARCHAR(10) UNIQUE,
    marca VARCHAR(50),
    modelo VARCHAR(50),
    numero_serie VARCHAR(50) UNIQUE,
    estado ENUM('DISPONIBLE','EN_FAENA','EN_MANTENIMIENTO', 'INTERNO') NOT NULL DEFAULT 'DISPONIBLE',
    horometro_actual DECIMAL(10,1) DEFAULT 0.0,
    telemetria_id VARCHAR(40) NULL, --referencia indirecta. para futuras implementaciones.
    CONSTRAINT fk_equipo_tipo FOREIGN KEY (id_tipo_equipo) REFERENCES tipo_equipo(id_tipo_equipo)
); --La información de cada equipo, el inventario.

CREATE TABLE plan_mantencion (
    id_plan INT UNSIGNED AUTO_INCREMENT PRIMARY KEY, 
    id_tipo_equipo SMALLINT UNSIGNED NOT NULL,
    nombre VARCHAR(80) NOT NULL,
    CONSTRAINT fk_plan_tipo_equipo FOREIGN KEY (id_tipo_equipo) REFERENCES tipo_equipo(id_tipo_equipo)
); --"Un plan de mantención pertenece a un tipo de equipo, pero un tipo de equipo puede tener varios planes"

CREATE TABLE servicio_plan (
    id_servicio_plan INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    id_plan INT UNSIGNED NOT NULL,
    nombre VARCHAR(60) NOT NULL,
    intervalo_horas INT UNSIGNED,
    descripcion TEXT,
    CONSTRAINT fk_servicio_plan FOREIGN KEY (id_plan) REFERENCES plan_mantencion(id_plan)
); --Permite distinguir entre una mantención de 250h y una de 1000h

--*Esto creará el catálogo de mantenciones disponibles y servirá como "ingrediente" para la "receta" del calculo de la mantencion.

CREATE TABLE insumo (
    id_insumo INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    codigo VARCHAR(30) UNIQUE NOT NULL,
    nombre VARCHAR(100) NOT NULL,
    unidad_medida VARCHAR(20)
);
--"El catalogo de insumos utilizados en la mantención de un equipo." (Antes se considero el stock, pero los requerimientos indicaron que no se gestiona esa información.)

CREATE TABLE servicio_plan_insumo (
    id_servicio_plan INT UNSIGNED NOT NULL,
    id_insumo INT UNSIGNED NOT NULL,
    cantidad DECIMAL(10,2) NOT NULL,
    PRIMARY KEY (id_servicio_plan, id_insumo),
    CONSTRAINT fk_spi_servicio FOREIGN KEY (id_servicio_plan) REFERENCES servicio_plan(id_servicio_plan),
    CONSTRAINT fk_spi_insumo FOREIGN KEY (id_insumo) REFERENCES insumo(id_insumo)
);

--*Reemplaza la "PAUTA INSUMOS". Aquí está la "receta" (qué se necesita para 250h, 500h, etc.(cruzas los datos)).

CREATE TABLE arriendo (
    id_arriendo INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    id_equipo INT UNSIGNED NOT NULL,
    id_cliente INT UNSIGNED NOT NULL,
    fecha_inicio DATE NOT NULL,
    fecha_termino DATE,
    CONSTRAINT fk_arriendo_equipo FOREIGN KEY (id_equipo) REFERENCES equipo(id_equipo),
    CONSTRAINT fk_arriendo_cliente FOREIGN KEY (id_cliente) REFERENCES cliente(id_cliente)
); --"Contrato de arriendo de un equipo a un cliente."

CREATE TABLE lectura_horometro (
    id_lectura BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    id_equipo INT UNSIGNED NOT NULL,
    id_usuario INT UNSIGNED NOT NULL,
    valor DECIMAL(10,1) NOT NULL,
    fecha_hora DATETIME NOT NULL,
    fuente ENUM('CLIENTE','TECNICO','PLANIFICACION','TELEMETRIA') NOT NULL,
    validada TINYINT(1) DEFAULT 0,
    observacion VARCHAR(255),
    CONSTRAINT fk_lectura_equipo FOREIGN KEY (id_equipo) REFERENCES equipo(id_equipo),
    CONSTRAINT fk_lectura_usuario FOREIGN KEY (id_usuario) REFERENCES usuario(id_usuario)
); --Historial de horas reales reportadas por el cliente o técnico.

--*Reemplaza la columna "Horómetro" del Excel. Esto permitirá construir el historial de uso y calcular automáticamente cuándo toca la próxima mantención.--

CREATE TABLE solicitud_horometro (
    id_solicitud INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    id_equipo INT UNSIGNED NOT NULL,
    id_cliente INT UNSIGNED NOT NULL,
    id_usuario_solicita INT UNSIGNED NOT NULL,
    fecha_solicitud DATETIME NOT NULL,
    estado ENUM('PENDIENTE','CUMPLIDA','VENCIDA') NOT NULL DEFAULT 'PENDIENTE',
    id_lectura BIGINT UNSIGNED UNIQUE,
    CONSTRAINT fk_solicitud_equipo FOREIGN KEY (id_equipo) REFERENCES equipo(id_equipo),
    CONSTRAINT fk_solicitud_cliente FOREIGN KEY (id_cliente) REFERENCES cliente(id_cliente),
    CONSTRAINT fk_solicitud_usuario FOREIGN KEY (id_usuario_solicita) REFERENCES usuario(id_usuario),
    CONSTRAINT fk_solicitud_lectura FOREIGN KEY (id_lectura) REFERENCES lectura_horometro(id_lectura)
); --Petición enviada al cliente para que reporte su horómetro.

--*Reemplaza los correos/WhatsApp pidiendo la hora. Esto permitirá construir el flujo de comunicación y alertas tempranas con el cliente.--

CREATE TABLE orden_trabajo (
    id_ot INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    id_equipo INT UNSIGNED NOT NULL,
    id_servicio_plan INT UNSIGNED NULL,
    tipo ENUM('PREVENTIVA', 'CORRECTIVA') NOT NULL,
    estado ENUM('PROGRAMADA','EN_CURSO','CERRADA') NOT NULL DEFAULT 'PROGRAMADA',
    numero_ot VARCHAR(20) UNIQUE NOT NULL, --*Para guardar el "89867"
    fecha_programada DATE,
    fecha_ejecucion DATE,
    horometro_cierre DECIMAL(10,1),
    observaciones TEXT,
    CONSTRAINT fk_ot_equipo FOREIGN KEY (id_equipo) REFERENCES equipo(id_equipo),
    CONSTRAINT fk_ot_servicio FOREIGN KEY (id_servicio_plan) REFERENCES servicio_plan(id_servicio_plan)
); -- Registro de la mantención ejecutada (la OT)

--*Reemplaza toda la planilla V168, ya que permite crear la trazabilidad que tiene el ejemplo "PLANILLA V168". Solo preguntas por todas las OT de una maquina.

CREATE TABLE orden_trabajo_insumo (
    id_ot INT UNSIGNED NOT NULL,
    id_insumo INT UNSIGNED NOT NULL,
    cantidad_usada DECIMAL(10,2) NOT NULL,
    notas VARCHAR(255), --*Porque cuando el técnico está en terreno ejecutando la OT, pueden pasar imprevistos (Ej: "REVISAR Y CAMBIAR CORREAS SEGÚN CONDICIONES", "")
    PRIMARY KEY (id_ot, id_insumo),
    CONSTRAINT fk_oti_ot FOREIGN KEY (id_ot) REFERENCES orden_trabajo(id_ot),
    CONSTRAINT fk_oti_insumo FOREIGN KEY (id_insumo) REFERENCES insumo(id_insumo)
); --Insumos reales usados en una OT.


CREATE TABLE auditoria (
    id_auditoria BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    id_usuario INT UNSIGNED NOT NULL,
    fecha_hora DATETIME(3) NOT NULL,
    entidad VARCHAR(40) NOT NULL,
    id_registro BIGINT UNSIGNED NOT NULL,
    operacion ENUM('INSERT','UPDATE','DELETE') NOT NULL,
    valor_anterior JSON,
    valor_nuevo JSON,
    ip VARCHAR(45),
    CONSTRAINT fk_auditoria_usuario FOREIGN KEY (id_usuario) REFERENCES usuario(id_usuario)
);--Auditoria DML

CREATE TABLE archivo_adjunto (
    id_archivo INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    id_usuario_subio INT UNSIGNED NOT NULL,
    entidad VARCHAR(40) NOT NULL,
    id_registro BIGINT UNSIGNED NOT NULL,
    nombre_original VARCHAR(255) NOT NULL,
    ruta VARCHAR(500) NOT NULL,
    mime VARCHAR(100), --Multipurpose Internet Mail Extensions (el tipo del archivo.)
    subido_en DATETIME DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_archivo_usuario FOREIGN KEY (id_usuario_subio) REFERENCES usuario(id_usuario)
); --Esta tabla se encarga de gestionar los archivos adjuntos. (sin soft-delete o delete cascade porque el backend se encargará de borrar al borrar algo.)

CREATE TABLE notificacion (
    id_notificacion BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    id_usuario_destino INT UNSIGNED NOT NULL,
    id_equipo INT UNSIGNED,
    tipo VARCHAR(30) NOT NULL,
    contenido JSON,
    estado ENUM('PENDIENTE','ENVIADA','ERROR'),
    enviada_en DATETIME,
    CONSTRAINT fk_notificacion_usuario FOREIGN KEY (id_usuario_destino) REFERENCES usuario(id_usuario),
    CONSTRAINT fk_notificacion_equipo FOREIGN KEY (id_equipo) REFERENCES equipo(id_equipo)
);  
-- Nota: Esta tabla no se usa en el MVP pero sirve para futuras implementaciones multi-canal

CREATE TABLE telemetria_equipo (
    id_telemetria BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    id_equipo INT UNSIGNED NOT NULL,
    ts DATETIME NOT NULL,
    horometro DECIMAL(10,1),
    payload JSON,
    CONSTRAINT fk_telemetria_equipo FOREIGN KEY (id_equipo) REFERENCES equipo(id_equipo)
); -- NOTA: Tabla fuera del alcance del MVP. Se conserva para futura integración de telemetría IoT. 

--*Esta tabla tampoco se usa porque no tenemos acceso a su telemetría, pero si nos la dan, se puede implementar
