# Factureo (Versión con Dashboard)

Aplicación web de gestión (Inventario, Clientes, Ventas) con Flask + MongoDB Atlas + Bootstrap 5.

## Requisitos
- Python 3.10+ (recomendado)
- Cuenta de MongoDB Atlas y cadena de conexión (MONGO_URI)
- PowerShell (Windows)

## Estructura
- app.py: servidor principal Flask
- config.py: configuración y carga de variables de entorno
- db.py: conexión a MongoDB y helper de colecciones
- modules/
  - usuarios.py: registro, login, logout (flask-login)
  - inventario.py: CRUD productos
  - clientes.py: CRUD clientes
  - ventas.py: registro y listado de ventas
- templates/: HTML con Bootstrap 5
- static/css/style.css: paleta y fuentes personalizadas
- .env.example: variables de entorno ejemplo
- requirements.txt: dependencias

## Configuración rápida (PowerShell)

1. Crear y activar entorno virtual

```powershell
cd "C:\Users\forer\Documents\2. Bases de datos masivas\factureo\factureo_backend"
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2. Instalar dependencias

```powershell
pip install -r requirements.txt
```

3. Crear archivo .env (copiar del ejemplo y editar)

```powershell
Copy-Item .env.example .env
# Edita .env para colocar tu cadena MONGO_URI de MongoDB Atlas y SECRET_KEY
```

4. Ejecutar en desarrollo

```powershell
$env:FLASK_APP="app.py"; $env:FLASK_ENV="development"; python app.py
```

App por defecto en http://127.0.0.1:5000/

## Configuración de correo (SMTP)

Para enviar comprobantes de nómina por correo, configura estas variables en `factureo_backend/.env`:

- MAIL_SERVER: servidor SMTP (ej. smtp.gmail.com, smtp.office365.com)
- MAIL_PORT: puerto (587 con TLS en la mayoría de casos)
- MAIL_USE_TLS: 1 si usa TLS al iniciar (STARTTLS), 0 en caso contrario
- MAIL_USERNAME: usuario de autenticación (si aplica)
- MAIL_PASSWORD: contraseña o App Password (Gmail/Office)
- MAIL_SENDER: dirección remitente (si no se define, usa MAIL_USERNAME)

Ejemplos rápidos:

Gmail (requiere 2FA + App Password):

```env
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=1
MAIL_USERNAME=tu_usuario@gmail.com
MAIL_PASSWORD=tu_app_password
MAIL_SENDER=tu_usuario@gmail.com
```

Office 365:

```env
MAIL_SERVER=smtp.office365.com
MAIL_PORT=587
MAIL_USE_TLS=1
MAIL_USERNAME=tu_usuario@tu_dominio.com
MAIL_PASSWORD=tu_contraseña_o_app_password
MAIL_SENDER=tu_usuario@tu_dominio.com
```

Desarrollo local con smtp4dev (no envía correos reales):

```env
MAIL_SERVER=localhost
MAIL_PORT=25
MAIL_USE_TLS=0
MAIL_SENDER=factureo@localhost
```

Luego, en el comprobante de nómina, usa “Enviar por correo”. Si falta configuración o hay un problema de conexión/autenticación, verás un mensaje con la causa.

## Notas sobre MongoDB Atlas
- Crea un clúster gratuito.
- Crea un usuario de base de datos y anota usuario/contraseña.
- En Network Access, permite tu IP o 0.0.0.0/0 (solo para desarrollo).
- Usa la conexión tipo "mongodb+srv://" en MONGO_URI.

## Próximos pasos
- Añadir validaciones más robustas (WTForms/Flask-WTF si se requiere CSRF).
- Exponer API REST para consumo por React en el futuro.