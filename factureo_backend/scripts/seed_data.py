import os
import sys
from werkzeug.security import generate_password_hash
from datetime import datetime

# Asegurar que el directorio factureo_backend esté en sys.path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from db import collection, ObjectId

# Usuario demo
if not collection('users').find_one({'email': 'demo@factureo.local'}):
    collection('users').insert_one({
        'name': 'Usuario Demo',
        'email': 'demo@factureo.local',
        'username': 'demo',
        'password': generate_password_hash('demo1234')
    })
    print('Usuario demo creado: demo@factureo.local / demo1234')

# Productos demo
productos_demo = [
    {'nombre': 'Cuaderno A5', 'cantidad': 120, 'precio': 3.5, 'categoria': 'Papelería'},
    {'nombre': 'Bolígrafo Azul', 'cantidad': 300, 'precio': 0.8, 'categoria': 'Papelería'},
    {'nombre': 'Resaltador', 'cantidad': 150, 'precio': 1.2, 'categoria': 'Papelería'},
    {'nombre': 'Mouse USB', 'cantidad': 40, 'precio': 8.9, 'categoria': 'Tecnología'},
    {'nombre': 'Teclado', 'cantidad': 25, 'precio': 12.5, 'categoria': 'Tecnología'}
]

for p in productos_demo:
    if not collection('productos').find_one({'nombre': p['nombre']}):
        collection('productos').insert_one(p)

print('Productos demo cargados.')

# Clientes demo
clientes_demo = [
    {'nombre': 'Acme S.A.', 'correo': 'compras@acme.com', 'telefono': '3000000001', 'direccion': 'Calle 123 #45-67'},
    {'nombre': 'Globex Ltd.', 'correo': 'hello@globex.co', 'telefono': '3000000002', 'direccion': 'Av. Siempre Viva 742'},
    {'nombre': 'Soylent Corp.', 'correo': 'ventas@soylent.io', 'telefono': '3000000003', 'direccion': 'Cra 10 #20-30'}
]

cliente_ids = []
for c in clientes_demo:
    existing = collection('clientes').find_one({'correo': c['correo']})
    if existing:
        cliente_ids.append(existing['_id'])
    else:
        res = collection('clientes').insert_one(c)
        cliente_ids.append(res.inserted_id)

print('Clientes demo cargados.')

# Venta demo
prod_ids = [doc['_id'] for doc in collection('productos').find().limit(3)]
if prod_ids and cliente_ids:
    collection('ventas').insert_one({
        'cliente_id': cliente_ids[0],
        'productos': prod_ids,
        'total': sum(float(collection('productos').find_one({'_id': pid})['precio']) for pid in prod_ids),
        'fecha': datetime.utcnow()
    })
    print('Venta demo registrada.')

print('Seed completado.')
