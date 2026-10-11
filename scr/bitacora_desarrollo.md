##Bitacora de desarrollo del proyecto Django Vilas Motor
Autor: Francisco Vera. 
Este documento no debe entregarse en la entrega del MVP, es para los integrantes del grupo. Para que Daniel compare cambios respecto a los UML. Para que Rodrigo analice qué redactar en cada punto y para que Marcos cuadre el roadmap donde todos trabajamos en el desarrollo para el cronograma Microsoft Proyect. 

##Jerarquía de bitacoras:
Se nombrará de más vieja a más nueva.

-Diagramas UML pre-eliminares (png's)
-Esquema SQL depurado con su propia bitacora interpretado a partir del diag preliminar
-Boceto de clases depurado considerando al esquema SQL.
-Bitacoras_<prefijo_diagrama> 
-App.txt

#Precedencias importantes
El diagrama relacional preliminar dió vida al esquema SQL depurado, el esquema SQL permitió el discernimiento para la 
depuración y creación del mapeo de clases del diagrama de clases para que respetara el modelo de datos. 
El boceto de clases permitió el discenirmiento y comprensión de los demás diagramas, dando a luz a sus bitacoras.
Finalmente todos los diagramas anteriores ayudaron a la comprensión del nuevo alcance del MVP lo que permitió el 
diseño de aplicaciones para el backend django en app.txt

##Desarrollo de modelos

Según requerimientos... una vez creadas las bases de datos mediante las instrucciones del README,
y la redacción del .env que definió:
DB_NAME, DB_PASSWORD, DB_USER, DB_HOST, DEBUG y SECRET_KEY.

Posteriormente se decidió primero crear los modelos de cada aplicación, se detalla el proceso paso a paso llevado a cabo

#I.-Settings.py
1.-Se crearon las apps del proyecto y luego fueron añadidas.
2.-Preconfiguraciones de secret_key y debug.
3.-La base de datos MySQL fue configurada
4.-Directorio de templates y static conectadas
5.-Configuración de idioma y zona horaria
6.-Inicialización con de AUTH_USER_MODEL mediante un comentario, se deja en blanco hasta crear 'cuentas.Usuario'

#II.-cuentas/managers.py y cuentas/models.py

1.-Se creó un manager de usuario propio utilizando el patrón factory mediante BaseUserManager (custom user)
2.-Se creó el modelo para usuarios, roles, y clientes.
3.-En el manager se creó un sistema de anti-escalada para en caso de escalada de roles mediante insersión. (seguridad)
4.-Se descomenta el comentario de AUTH_USER_MODEL en settings.py ahora que se ha implementado los módulo.

Notas:

N.1: El planificador (único rol) administra: create_user fija is_staff=True.
N.2: PermissionsMixin agrega la columna is_superuser y las tablas M2M usuario_groups y usuario_user_permissions; is_staff se declara a mano.
Django suma además sus tablas propias (auth_group, auth_permission, django_content_type, django_session, django_migrations). Nada de esto está en schema.sql: es infraestructura del framework, no redundancia.
N.3: Ahora se entra con email, no con nombre de usuario. Además se forzó a Django a mantener los nombres del esquema en la base de datos. Las columnas siguen manteniendo sus nombres.

#III.-flota/models.py

1.-Se crea a partir del modelo al ORM
2.-Hallazgo: estado no tiene default, corregido en el esquema y documentado en la bitacora_esquema. Debe nacer disponible y debe ser no nulo. Implementado en el modelo.

#IV.- insumos/models.py & arriendos/models.py

1.-Se crean respetando las reglas de negocio.

N.1: Arriendo tiene FK' s de Cliente y flota, asi que se implementa correctamente.
N.2: fecha_termino nullable = la señal de "vigente". Null significa arriendo abierto. No hay campo estado: la vigencia se infiere.

#V.- horometros/models.py

1.-Se crea el modelo
2.-Hallazgo: atributo 'fuente' debe ser no nulo y el atributo 'estado' debe tener el estado por default "pendiente". Se actualizó el schema.sql y se agregó un punto en su bitacora.


#VI.- mantencion/models.py

1.-Se crea el modelo siguiendo la documentación y modelos anteriores.
2.-Hallazgo menor sobre sintaxis erronea en el schemaSQL
3.- atributo "tipo" modelado como NOT NULL sin default: el planificador elige preventiva o correctiva
al crear la OT

N.1:PK compuesta. El schema usa PRIMARY KEY (id_servicio_plan, id_insumo) y (id_ot, id_insumo). Django no soporta PK compuesta. Lo resolví con UniqueConstraint + on_delete=CASCADE. Consecuencia honesta: Django agregará una columna id extra y la clave será UNIQUE, no PRIMARY KEY. No hay forma limpia de
evitarlo.

#VII.- auditoria/models.py

1.-Se crea los modelos Auditoria y ArchivoAdjunto
2.-Hallazgo: 'id_registro' no es fk, es una referencia genérica(out-scoping) Se modeló como BigIhtegerField.
3.-'ruta' se cambia de CharField a FileField para la gestión real de archivos y exportaciones.
4.-Se configura MEDIA_ROOT y MEDIA_URL en settings.py, y el serving de media en urls.py (media serving se activa solo en debug; en producción lo sirve el servidor web.)

N.1: FileField(upload_to='adjuntos/', max_length=500) sigue mapeando. VARCHAR(500)
N.2:nombre_original y mime se conservan aunque FileField exponga name y content_type: guardan el nombre humano y el MIME explícito, que FileField no persiste.

#VIII.- Migración de los modelos para validar

1.-Se migran los modelos para validar sus referencias cruzadas, dando todas éxito. 
(python manage.py makemigrations, luego migrate)

#IX.- Lógica de dominio, servicios y pruebas

1.-Se trasladan los métodos de dominio restantes del boceto de clases (classes.py) a modelos ORM:

-Equipo (cambiarEstado, actualizarHorometro, ultimaLectura), PlanMantencion(serviciosOrdenados)
-ServicioPlan (insumosRequeridos)
-Arriendo (cerrar, estaVigente)
-SolicitudHorometro (cumplir, marcarVencida)
-OrdenTrabajo (programar, registrarInsumo, cerrar).

2.-Se descartaron los métodos autenticación, set_password, save, permisos y los de fuera de alcance(stock, notificación, telemetria) por que django los cobre o están fuera de scope.

3.-Se crea el servicio puro CalculadoraProximoServicio en mantencion/services.py

4.-Se crea el servicio puro ValidadorDatos en horometros/services.py

5.Población de pruebas: se escribieron 20 tests en flota, mantención, horometros y arrendos que validan métodos y servicios. 20/20 aprobados en todos. (usar pyhton manage.py test)

N.1: ValidadorDatos rechaza lecturas negativas o menores al horómetro actual (el horómetro no retrocede).

N.2: CalculadoraProximoServicio define "próximo servicio" como el de menos horas restantes: intervalo − (horómetro_actual − último cierre de OT de ese servicio). 

N.3: Los servicios no son tablas: viven en services.py y no generan migración (makemigrations --check reportó "sin cambios").

N.4: OrdenTrabajo.cerrar() también fija fecha_ejecucion, dato que el boceto omitía.

#X.-Registro de CRUDs en admin.py de las aplicaciones y superusuario

1.-Se registran los 16 modelos en los admin.py de las 7 apps 
2.-Hallazgo: nuestro create_superuser exige que exista el rol planificador en la tabla rol Se crea el módulo de data migration 'seed_rol_planificador' en cuentas/migrations con el fin de sembrar el rol planificador con get_or_create, asegurando su existencia al hacer migrate.

3.-Se crea el superusuario con las siguientes credenciales:
-email: test@vilasmotor.cl
-Nombre: Planificador
-Password: Seguridad2026!

#XI.- Vistas de listado, templates y navegación

1.-Se crearon las vistas de listado de las 6 apps (equipos, tipos, insumos, solicitudes, lecturas, arriendos, planes, OT, clientes, catálogos, home y dashboard); todas responden 200.
2.-Se creó base.html (header con logo y nav, footer) y los templates de cada listado, conectados con namespaces ({% url 'app:nombre' %}).
3.-El dashboard usa CalculadoraProximoServicio con un umbral de alerta (100 horas) para marcar equipos en alerta.

#XII.- Login y protección de vistas

1.-Login por email (LoginForm + LoginView/LogoutView), con LOGIN_URL apuntando al login propio.
2.-Se protegió todo el sistema con LoginRequiredMiddleware: toda vista pide login; login, logout y admin quedan exentos.
3.-El header muestra "Entrar"/"Cerrar sesión" según la sesión.

#XIII.- Forms de escritura y alta de catálogos

1.-Horómetros: solicitar lectura y registrar lectura (ValidadorDatos rechaza el retroceso del horómetro).
2.-Arriendos: crear y cerrar (rechaza re-arrendar un equipo ya vigente).
3.-Órdenes de trabajo: crear (número auto OT-0001...), registrar insumo y cerrar.
4.-Alta de catálogos en la app: cliente, tipo de equipo, equipo, insumo, plan y servicio (sin depender del admin).
5.-Detalle de equipo: ficha con historial (lecturas, OT, arriendos) y botones de acción.

#XIV.- Pruebas

1.-Se ampliaron los tests de 20 a 35, cubriendo vistas de escritura, alta de catálogos y detalle de equipo. 35/35 aprobados.

N.1: numero_ot se genera automáticamente al crear la OT (OT-0001, OT-0002...).
N.2: arriendo con fecha_termino nula = vigente (regla ya documentada en IV).
