import os
import sys
import types

# Asegurar que factureo_backend esté en sys.path para importar app
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from app import create_app

def test_app_factory_creates_app():
    app = create_app()
    assert app is not None


def test_index_route_returns_200():
    app = create_app()
    client = app.test_client()
    resp = client.get('/')
    assert resp.status_code == 200
