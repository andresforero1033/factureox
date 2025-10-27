from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from db import collection, ObjectId

clientes_bp = Blueprint('clientes', __name__)


@clientes_bp.route('/')
@login_required
def list_clients():
    owner_id = ObjectId(current_user.id)
    q = {'owner_id': owner_id}
    term = (request.args.get('q') or '').strip()
    estado = (request.args.get('estado') or '').strip()
    if term:
        q['$or'] = [
            {'nombre': {'$regex': term, '$options': 'i'}},
            {'correo': {'$regex': term, '$options': 'i'}},
            {'telefono': {'$regex': term, '$options': 'i'}},
            {'identificacion': {'$regex': term, '$options': 'i'}},
        ]
    if estado:
        q['estado'] = estado
    clientes = list(collection('clientes').find(q).sort('nombre', 1))
    return render_template('clientes.html', clientes=clientes)


@clientes_bp.route('/crear', methods=['POST'])
@login_required
def create_client():
    nombre = request.form.get('nombre', '').strip()
    correo = request.form.get('correo', '').strip().lower()
    telefono = request.form.get('telefono', '').strip()
    direccion = request.form.get('direccion', '').strip()
    identificacion = (request.form.get('identificacion') or '').strip()
    estado = (request.form.get('estado') or 'activo').strip().lower()

    if not nombre or not correo:
        flash('Nombre y correo son obligatorios', 'warning')
        return redirect(url_for('clientes.list_clients'))

    collection('clientes').insert_one({
        'nombre': nombre,
        'correo': correo,
        'telefono': telefono,
        'direccion': direccion,
        'identificacion': identificacion or None,
        'estado': estado,
        'owner_id': ObjectId(current_user.id)
    })
    flash('Cliente creado', 'success')
    return redirect(url_for('clientes.list_clients'))


@clientes_bp.route('/editar/<id>', methods=['POST'])
@login_required
def edit_client(id):
    nombre = request.form.get('nombre', '').strip()
    correo = request.form.get('correo', '').strip().lower()
    telefono = request.form.get('telefono', '').strip()
    direccion = request.form.get('direccion', '').strip()
    identificacion = (request.form.get('identificacion') or '').strip()
    estado = (request.form.get('estado') or 'activo').strip().lower()

    owner_id = ObjectId(current_user.id)
    collection('clientes').update_one({'_id': ObjectId(id), 'owner_id': owner_id}, {
        '$set': {
            'nombre': nombre,
            'correo': correo,
            'telefono': telefono,
            'direccion': direccion,
            'identificacion': identificacion or None,
            'estado': estado
        }
    })
    flash('Cliente actualizado', 'success')
    return redirect(url_for('clientes.list_clients'))


@clientes_bp.route('/eliminar/<id>', methods=['POST'])
@login_required
def delete_client(id):
    owner_id = ObjectId(current_user.id)
    collection('clientes').delete_one({'_id': ObjectId(id), 'owner_id': owner_id})
    flash('Cliente eliminado', 'info')
    return redirect(url_for('clientes.list_clients'))
