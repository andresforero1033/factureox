#!/usr/bin/env python
import sys
from pathlib import Path
import argparse
from typing import List

# Asegurar imports del paquete backend
BASE_DIR = Path(__file__).resolve().parents[1]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from db import collection, ObjectId  # type: ignore

COLLECTIONS = ['productos', 'clientes', 'ventas', 'empleados', 'nomina']


def backfill(user_id: ObjectId, collections: List[str], dry_run: bool = False) -> None:
    for name in collections:
        coll = collection(name)
        q = {'$or': [{'owner_id': {'$exists': False}}, {'owner_id': None}]}
        count = coll.count_documents(q)
        if count == 0:
            print(f"[{name}] No hay documentos sin owner_id.")
            continue
        if dry_run:
            print(f"[{name}] DRY-RUN: {count} documentos serían actualizados con owner_id={user_id}.")
            continue
        res = coll.update_many(q, {'$set': {'owner_id': user_id}})
        print(f"[{name}] Actualizados {res.modified_count}/{count} documentos con owner_id={user_id}.")


def main():
    p = argparse.ArgumentParser(description='Asigna owner_id a documentos históricos.')
    p.add_argument('--user-id', help='ObjectId del usuario propietario', default=None)
    p.add_argument('--collections', nargs='*', default=COLLECTIONS, help=f'Colecciones a procesar. Por defecto: {", ".join(COLLECTIONS)}')
    p.add_argument('--dry-run', action='store_true', help='No escribe cambios, solo muestra lo que haría')
    args = p.parse_args()

    if not args.user_id:
        print('Error: Debes proporcionar --user-id (ObjectId del usuario destino).')
        sys.exit(2)

    try:
        user_oid = ObjectId(args.user_id)
    except Exception:
        print('Error: --user-id no es un ObjectId válido.')
        sys.exit(2)

    cols = [c for c in args.collections if c in COLLECTIONS]
    if not cols:
        print('No se especificaron colecciones válidas. Usa: productos clientes ventas empleados nomina')
        sys.exit(2)

    backfill(user_oid, cols, dry_run=args.dry_run)


if __name__ == '__main__':
    main()
