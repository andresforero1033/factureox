# Factureo

Aplicación web de gestión empresarial con Flask + MongoDB Atlas + Bootstrap 5.

## Módulos
- Autenticación (registro, login, logout)
- Inventario (productos)
- Clientes
- Ventas
- Dashboard con accesos rápidos

## Requisitos
- Python 3.10+
- Cuenta en MongoDB Atlas (cadena de conexión)
- PowerShell en Windows (o terminal equivalente)

## Estructura
- `factureo_backend/`
  - `app.py`: servidor Flask
  - `config.py`: configuración y lectura de `.env`
  - `db.py`: conexión a MongoDB
  - `modules/`: usuarios, inventario, clientes, ventas
  - `templates/`: HTML + Bootstrap
  - `static/css/style.css`
  - `scripts/`: utilidades (init_db, seed_data)
  - `requirements.txt`: dependencias
  - `requirements-dev.txt`: deps de desarrollo (pytest, ruff)

## Pasos de ejecución (local)
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

3. Configurar `.env`
Crea `factureo_backend/.env` con:
```
MONGO_URI=mongodb+srv://<usuario>:<password>@<cluster>.mongodb.net/factureo?retryWrites=true&w=majority&appName=<TuCluster>
SECRET_KEY=<una-clave-aleatoria>
SESSION_COOKIE_NAME=factureo_session
```

4. Inicializar índices (opcional)
```powershell
python .\scripts\init_db.py
```

5. Ejecutar servidor
```powershell
python app.py
```
Abre http://127.0.0.1:5000

## Conectar a MongoDB Atlas
- Crea/usa un clúster (Cluster0)
- Database Access: crea usuario con rol `readWrite` sobre BD `factureo`
- Network Access: añade tu IP o 0.0.0.0/0 (solo dev)
- Usa la URI con `/factureo` al final (BD por defecto)

## Datos de ejemplo (seed)
Para cargar datos de ejemplo:
```powershell
# Instala dependencias (si no lo has hecho)
pip install -r requirements.txt
python .\scripts\seed_data.py
```
Esto añade productos, clientes, un usuario demo y ventas de prueba.

## Desarrollo: lint y tests
Instala deps de desarrollo y ejecuta:
```powershell
pip install -r requirements-dev.txt
# Lint (ruff)
ruff check .
# Tests (pytest)
pytest -q
```

## CI (GitHub Actions)
Se incluye un workflow en `.github/workflows/ci.yml` que:
- Instala dependencias
- Ejecuta ruff (lint)
- Ejecuta pytest

## Troubleshooting
- Si la app intenta conectar a `localhost:27017`, revisa que `.env` esté correcto y que `config.py` cargue `.env` (ya incluido).
- Si ves `Authentication failed`, revisa usuario/clave de Atlas y tu IP en Network Access.
- Si cambiaste la contraseña en Atlas, actualiza el `.env`.
