import os
from pathlib import Path
from dotenv import load_dotenv

_ENV_PATH = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=_ENV_PATH)

def _get_mongo_uri():
    uri = os.getenv("MONGO_URI")
    # Si está definida pero vacía, usa el valor por defecto local
    if not uri:
        return "mongodb://localhost:27017/factureo"
    return uri

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")
    SESSION_COOKIE_NAME = os.getenv("SESSION_COOKIE_NAME", "factureo_session")
    MONGO_URI = _get_mongo_uri()
    DEBUG = os.getenv("FLASK_DEBUG", "1") == "1"
    # OAuth (configurar por variables de entorno)
    GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
    GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
    MICROSOFT_CLIENT_ID = os.getenv("MICROSOFT_CLIENT_ID")
    MICROSOFT_CLIENT_SECRET = os.getenv("MICROSOFT_CLIENT_SECRET")
    # Multi-tenant (common) por defecto
    MS_TENANT = os.getenv("MS_TENANT", "common")
    # Nómina (Colombia) - configurables por entorno
    # Salario mínimo mensual legal vigente (SMLMV) y Auxilio de transporte
    # Valores por defecto razonables para desarrollo; ajusta en .env
    COL_SMMLV = int(os.getenv("COL_SMMLV", "1300000"))
    COL_AUX_TRANSPORTE = int(os.getenv("COL_AUX_TRANSPORTE", "162000"))
    # Email (SMTP)
    MAIL_SERVER = os.getenv("MAIL_SERVER")
    MAIL_PORT = int(os.getenv("MAIL_PORT", "587"))
    MAIL_USE_TLS = os.getenv("MAIL_USE_TLS", "1") == "1"
    MAIL_USERNAME = os.getenv("MAIL_USERNAME")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
    MAIL_SENDER = os.getenv("MAIL_SENDER", os.getenv("MAIL_USERNAME", "factureo@localhost"))

config = Config()
