from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from db import collection, ObjectId

inventario_bp = Blueprint('inventario', __name__)


@inventario_bp.route('/')
@login_required
def list_products():
    productos = list(collection('productos').find())
    return render_template('inventario.html', productos=productos)


@inventario_bp.route('/crear', methods=['POST'])
@login_required
def create_product():
    nombre = request.form.get('nombre', '').strip()
    cantidad = int(request.form.get('cantidad', '0') or 0)
    precio = float(request.form.get('precio', '0') or 0)
    categoria = request.form.get('categoria', '').strip()

    if not nombre or cantidad < 0 or precio < 0:
        flash('Datos inválidos', 'warning')
        return redirect(url_for('inventario.list_products'))

    collection('productos').insert_one({
        'nombre': nombre,
        'cantidad': cantidad,
        'precio': precio,
        'categoria': categoria
    })
    flash('Producto creado', 'success')
    return redirect(url_for('inventario.list_products'))


@inventario_bp.route('/editar/<id>', methods=['POST'])
@login_required
def edit_product(id):
    nombre = request.form.get('nombre', '').strip()
    cantidad = int(request.form.get('cantidad', '0') or 0)
    precio = float(request.form.get('precio', '0') or 0)
    categoria = request.form.get('categoria', '').strip()

    collection('productos').update_one({'_id': ObjectId(id)}, {
        '$set': {
            'nombre': nombre,
            'cantidad': cantidad,
            'precio': precio,
            'categoria': categoria
        }
    })
    flash('Producto actualizado', 'success')
    return redirect(url_for('inventario.list_products'))


@inventario_bp.route('/eliminar/<id>', methods=['POST'])
@login_required
def delete_product(id):
    collection('productos').delete_one({'_id': ObjectId(id)})
    flash('Producto eliminado', 'info')
    return redirect(url_for('inventario.list_products'))
