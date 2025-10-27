#!/usr/bin/env python
import sys
from pathlib import Path

# Asegurar imports del paquete backend
BASE_DIR = Path(__file__).resolve().parents[1]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from db import db  # type: ignore


def ensure():
    # Productos
    db['productos'].create_index('owner_id', name='owner_id_1')

    # Clientes
    db['clientes'].create_index('owner_id', name='owner_id_1')
    db['clientes'].create_index('correo', name='correo_1')

    # Ventas
    db['ventas'].create_index([('owner_id', 1), ('fecha', -1)], name='owner_id_1_fecha_-1')

    # Empleados
    db['empleados'].create_index('owner_id', name='owner_id_1')
    db['empleados'].create_index('name', name='name_1')

    # Nómina
    db['nomina'].create_index([('owner_id', 1), ('period', -1)], name='owner_id_1_period_-1')
    db['nomina'].create_index('empleado_id', name='empleado_id_1')

    print('Índices creados/asegurados.')


if __name__ == '__main__':
    ensure()
