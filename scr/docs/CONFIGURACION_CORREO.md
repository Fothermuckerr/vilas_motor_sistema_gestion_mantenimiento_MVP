# Acceso por correo

El inicio de sesión identifica a cada usuario por su correo electrónico. El menú
**Usuarios** permite al personal del sistema crear cuentas con rol, cliente
opcional y contraseña inicial. Las cuentas creadas desde esta pantalla no
obtienen privilegios de superusuario.

El enlace de recuperación de contraseña vence en 24 horas. Durante el desarrollo
el correo se imprime en la consola del servidor. Para enviar correos reales,
agregue estas variables al archivo `.env`:

```env
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.tu-proveedor.cl
EMAIL_PORT=587
EMAIL_HOST_USER=usuario-smtp
EMAIL_HOST_PASSWORD=clave-smtp
EMAIL_USE_TLS=True
DEFAULT_FROM_EMAIL=noreply@tu-dominio.cl
```

Los códigos de equipos se pueden ingresar manualmente o generar de forma
automática. La generación usa el tipo de equipo y el siguiente correlativo
disponible, por ejemplo `GENERADO-001`.
