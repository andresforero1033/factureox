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

## Notas sobre MongoDB Atlas
- Crea un clúster gratuito.
- Crea un usuario de base de datos y anota usuario/contraseña.
- En Network Access, permite tu IP o 0.0.0.0/0 (solo para desarrollo).
- Usa la conexión tipo "mongodb+srv://" en MONGO_URI.

## Próximos pasos
- Añadir validaciones más robustas (WTForms/Flask-WTF si se requiere CSRF).
- Exponer API REST para consumo por React en el futuro.