##Django vilas_motor system

#Comandos para la instalación de requerimientos

```
$ python3 -m venv .venv
$ source .venv/bin/activate
$ pip install -r requirements.txt

```

#Comandos para inicializar la base de datos.

```

$ sudo systemctl start mysql  //(levantar mysql)
$ sudo mysql -e "CREATE DATABASE vilas_motor CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci" //(Creamos la db y establecemos su configuracion para simbolos.)
$ sudo mysql -e "CREATE USER 'vilas'@'localhost' IDENTIFIED BY '<CLAVE>'; GRANT ALL PRIVILEGES ON vilas_motor.* TO 'vilas'@'localhost'; FLUSH PRIVILEGES;"

```

#Creación de apps y proyecto
**Alcance MVP:** planificación de mantenciones, horómetros, OT, insumos, auditoría. 
**Out-scope:** stock, facturación, notificaciones, telemetría, técnico como actor.


```
django-admin startproject vilas_motor . (con el venv activo y descargado el requirements)

python manage.py startapp cuentas
python manage.py startapp flota
python manage.py startapp insumos
python manage.py startapp mantencion
python manage.py startapp horometros
python manage.py startapp arriendos
python manage.py startapp auditoria

```
