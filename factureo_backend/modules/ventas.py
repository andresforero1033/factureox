from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from db import collection, ObjectId
from datetime import datetime
import json

ventas_bp = Blueprint('ventas', __name__)


@ventas_bp.route('/')
@login_required
def list_sales():
    owner_id = ObjectId(current_user.id)
    q = {'owner_id': owner_id}
    # Filtros: rango de fechas, cliente, estado
    desde = request.args.get('desde') or ''
    hasta = request.args.get('hasta') or ''
    cliente = request.args.get('cliente') or ''
    estado = request.args.get('estado') or ''
    if cliente:
        try:
            q['cliente_id'] = ObjectId(cliente)
        except Exception:
            pass
    if estado:
        q['estado'] = estado
    if desde or hasta:
        q['fecha'] = {}
        if desde:
            try:
                q['fecha']['$gte'] = datetime.fromisoformat(desde)
            except Exception:
                pass
        if hasta:
            try:
                # incluir final del día si solo viene fecha
                q['fecha']['$lte'] = datetime.fromisoformat(hasta + ('T23:59:59' if 'T' not in hasta else ''))
            except Exception:
                pass
        if not q['fecha']:
            q.pop('fecha', None)

    ventas = list(collection('ventas').find(q).sort('fecha', -1))
    # Enriquecer con nombre de cliente
    clientes = list(collection('clientes').find({'owner_id': owner_id}))
    cliente_lookup = {str(c['_id']): c.get('nombre') for c in clientes}
    for v in ventas:
        v['cliente_nombre'] = cliente_lookup.get(str(v.get('cliente_id')), '—')

    productos = list(collection('productos').find({'owner_id': owner_id}))
    return render_template('ventas.html', ventas=ventas, clientes=clientes, productos=productos)


@ventas_bp.route('/crear', methods=['POST'])
@login_required
def create_sale():
    owner_id = ObjectId(current_user.id)
    cliente_id = request.form.get('cliente_id')
    items_json = request.form.get('items_json')
    descuento_pct = float(request.form.get('descuento_pct', '0') or 0)
    impuesto_pct = float(request.form.get('impuesto_pct', '0') or 0)

    if not cliente_id or not items_json:
        flash('Debe seleccionar un cliente y agregar al menos un producto.', 'warning')
        return redirect(url_for('ventas.list_sales'))

    # Validar cliente del usuario
    try:
        cli = collection('clientes').find_one({'_id': ObjectId(cliente_id), 'owner_id': owner_id})
    except Exception:
        cli = None
    if not cli:
        flash('Cliente inválido.', 'danger')
        return redirect(url_for('ventas.list_sales'))

    # Parsear items
    try:
        items = json.loads(items_json)
        assert isinstance(items, list)
    except Exception:
        flash('Carrito inválido.', 'danger')
        return redirect(url_for('ventas.list_sales'))

    # Calcular totales y validar stock
    subtotal = 0.0
    resolved_items = []
    productos_coll = collection('productos')
    for it in items:
        try:
            pid = ObjectId(it['producto_id'])
            qty = int(it.get('cantidad', 1))
            if qty <= 0:
                raise ValueError('Cantidad inválida')
        except Exception:
            flash('Item de producto inválido.', 'danger')
            return redirect(url_for('ventas.list_sales'))
        prod = productos_coll.find_one({'_id': pid, 'owner_id': owner_id})
        if not prod:
            flash('Producto no encontrado o no pertenece al usuario.', 'danger')
            return redirect(url_for('ventas.list_sales'))
        precio_unit = float(prod.get('precio_venta') or prod.get('precio') or 0)
        line_sub = precio_unit * qty
        subtotal += line_sub
        resolved_items.append({
            'producto_id': pid,
            'nombre': prod.get('nombre'),
            'precio_unitario': precio_unit,
            'cantidad': qty,
            'subtotal': round(line_sub, 2)
        })

    descuento_total = round(subtotal * (descuento_pct/100.0), 2)
    base_imponible = subtotal - descuento_total
    impuesto_total = round(base_imponible * (impuesto_pct/100.0), 2)
    total = round(base_imponible + impuesto_total, 2)

    # Descontar stock de forma atómica por item
    for it in resolved_items:
        res = collection('productos').update_one(
            {'_id': it['producto_id'], 'owner_id': owner_id, 'cantidad': {'$gte': it['cantidad']}},
            {'$inc': {'cantidad': -it['cantidad']}}
        )
        if res.matched_count == 0:
            flash(f"Stock insuficiente para {it['nombre']}.", 'danger')
            return redirect(url_for('ventas.list_sales'))

    sale_doc = {
        'cliente_id': ObjectId(cliente_id),
        'items': resolved_items,
        'subtotal': round(subtotal, 2),
        'descuento_pct': descuento_pct,
        'descuento_total': descuento_total,
        'impuesto_pct': impuesto_pct,
        'impuesto_total': impuesto_total,
        'total': total,
        'estado': 'completada',
        'fecha': datetime.utcnow(),
        'owner_id': owner_id
    }
    collection('ventas').insert_one(sale_doc)
    flash('Venta registrada correctamente.', 'success')
    return redirect(url_for('ventas.list_sales'))
