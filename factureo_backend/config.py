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

config = Config()
