from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from db import collection, ObjectId
from datetime import datetime

ventas_bp = Blueprint('ventas', __name__)


@ventas_bp.route('/')
@login_required
def list_sales():
    owner_id = ObjectId(current_user.id)
    ventas = list(collection('ventas').find({'owner_id': owner_id}).sort('fecha', -1))
    clientes = list(collection('clientes').find({'owner_id': owner_id}))
    productos = list(collection('productos').find({'owner_id': owner_id}))
    return render_template('ventas.html', ventas=ventas, clientes=clientes, productos=productos)


@ventas_bp.route('/crear', methods=['POST'])
@login_required
def create_sale():
    cliente_id = request.form.get('cliente_id')
    productos_ids = request.form.getlist('productos_ids')

    if not cliente_id or not productos_ids:
        flash('Debe seleccionar un cliente y al menos un producto', 'warning')
        return redirect(url_for('ventas.list_sales'))

    owner_id = ObjectId(current_user.id)
    # Validar que el cliente pertenece al usuario
    cli = collection('clientes').find_one({'_id': ObjectId(cliente_id), 'owner_id': owner_id})
    if not cli:
        flash('Cliente inválido.', 'danger')
        return redirect(url_for('ventas.list_sales'))

    productos = list(collection('productos').find({
        '_id': {'$in': [ObjectId(pid) for pid in productos_ids]},
        'owner_id': owner_id
    }))
    if not productos:
        flash('No se encontraron productos válidos para este usuario.', 'danger')
        return redirect(url_for('ventas.list_sales'))

    total = sum(float(p.get('precio', 0)) for p in productos)

    collection('ventas').insert_one({
        'cliente_id': ObjectId(cliente_id),
        'productos': [p.get('_id') for p in productos],
        'total': total,
        'fecha': datetime.utcnow(),
        'owner_id': owner_id
    })

    flash('Venta registrada', 'success')
    return redirect(url_for('ventas.list_sales'))
