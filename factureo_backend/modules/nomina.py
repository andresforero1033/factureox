from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, send_file
from flask_login import login_required
from db import collection, ObjectId
from datetime import datetime
from io import StringIO
import csv

nomina_bp = Blueprint('nomina', __name__)


def _now():
    return datetime.utcnow()


def _get_conf():
    cfg = current_app.config
    return {
        'SMMLV': int(cfg.get('COL_SMMLV', 1300000)),
        'AUX_TRANSPORTE': int(cfg.get('COL_AUX_TRANSPORTE', 162000)),
    }


@nomina_bp.route('/')
@login_required
def home():
    # Resumen simple: últimas liquidaciones por periodo
    runs = list(collection('nomina').aggregate([
        { '$sort': { 'period': -1, 'created_at': -1 } },
        { '$group': {
            '_id': '$period',
            'count': { '$sum': 1 },
            'total_neto': { '$sum': '$totals.neto' },
            'created_at': { '$first': '$created_at' }
        }},
        { '$sort': { '_id': -1 }},
        { '$limit': 12 }
    ]))
    for r in runs:
        r['period_str'] = str(r['_id'])
    return render_template('nomina_home.html', runs=runs)


@nomina_bp.route('/empleados')
@login_required
def empleados_list():
    empleados = list(collection('empleados').find({}).sort('name', 1))
    return render_template('nomina_empleados_list.html', empleados=empleados)


@nomina_bp.route('/empleados/nuevo', methods=['GET','POST'])
@login_required
def empleados_new():
    if request.method == 'POST':
        name = request.form.get('name','').strip()
        doc_id = request.form.get('document_id','').strip()
        position = request.form.get('position','').strip()
        base_salary = int(request.form.get('base_salary','0') or 0)
        contract_type = request.form.get('contract_type','indefinido')
        start_date = request.form.get('start_date')
        active = request.form.get('active') == 'on'
        eligible_transport = request.form.get('eligible_transport') == 'on'
        if not name or not doc_id or base_salary <= 0:
            flash('Nombre, documento y salario base son obligatorios.', 'warning')
            return render_template('nomina_empleados_form.html')
        doc = {
            'name': name,
            'document_id': doc_id,
            'position': position,
            'base_salary': base_salary,
            'contract_type': contract_type,
            'start_date': start_date,
            'active': active,
            'eligible_transport': eligible_transport,
            'created_at': _now()
        }
        res = collection('empleados').insert_one(doc)
        flash('Empleado creado.', 'success')
        return redirect(url_for('nomina.empleados_list'))
    return render_template('nomina_empleados_form.html')


@nomina_bp.route('/empleados/editar/<id>', methods=['GET','POST'])
@login_required
def empleados_edit(id):
    empleados = collection('empleados')
    emp = empleados.find_one({'_id': ObjectId(id)})
    if not emp:
        flash('Empleado no encontrado', 'danger')
        return redirect(url_for('nomina.empleados_list'))
    if request.method == 'POST':
        name = request.form.get('name','').strip()
        doc_id = request.form.get('document_id','').strip()
        position = request.form.get('position','').strip()
        base_salary = int(request.form.get('base_salary','0') or 0)
        contract_type = request.form.get('contract_type','indefinido')
        start_date = request.form.get('start_date')
        active = request.form.get('active') == 'on'
        eligible_transport = request.form.get('eligible_transport') == 'on'
        if not name or not doc_id or base_salary <= 0:
            flash('Nombre, documento y salario base son obligatorios.', 'warning')
            return render_template('nomina_empleados_form.html', emp=emp)
        empleados.update_one({'_id': emp['_id']}, {'$set': {
            'name': name,
            'document_id': doc_id,
            'position': position,
            'base_salary': base_salary,
            'contract_type': contract_type,
            'start_date': start_date,
            'active': active,
            'eligible_transport': eligible_transport,
            'updated_at': _now()
        }})
        flash('Empleado actualizado.', 'success')
        return redirect(url_for('nomina.empleados_list'))
    return render_template('nomina_empleados_form.html', emp=emp)


@nomina_bp.route('/generar', methods=['GET','POST'])
@login_required
def generar():
    conf = _get_conf()
    if request.method == 'POST':
        year = int(request.form.get('year') or 0)
        month = int(request.form.get('month') or 0)
        days = int(request.form.get('days') or 30)
        if not (2000 <= year <= 2100) or not (1 <= month <= 12):
            flash('Periodo inválido.', 'warning')
            return render_template('nomina_generar.html', conf=conf)
        period = int(f"{year:04d}{month:02d}")
        empleados = list(collection('empleados').find({'active': True}))
        if not empleados:
            flash('No hay empleados activos.', 'info')
            return render_template('nomina_generar.html', conf=conf)
        created = 0
        for emp in empleados:
            # Evitar duplicado del periodo por empleado
            exists = collection('nomina').find_one({'period': period, 'empleado_id': emp['_id']})
            if exists:
                continue
            base_salary = int(emp.get('base_salary', 0))
            propor = (base_salary * days) / 30.0
            aux = 0
            if emp.get('eligible_transport') and base_salary <= (conf['SMMLV'] * 2):
                aux = (conf['AUX_TRANSPORTE'] * days) / 30.0
            ibc = propor  # aproximación: IBC = salario proporcional, sin auxilio
            salud = round(ibc * 0.04)
            pension = round(ibc * 0.04)
            solidaridad = round(ibc * 0.01) if base_salary >= (conf['SMMLV'] * 4) else 0
            devengados = round(propor + aux)
            deducciones = salud + pension + solidaridad
            neto = devengados - deducciones
            doc = {
                'period': period,
                'year': year,
                'month': month,
                'days': days,
                'empleado_id': emp['_id'],
                'empleado': {
                    'name': emp.get('name'),
                    'document_id': emp.get('document_id'),
                    'position': emp.get('position'),
                    'base_salary': base_salary
                },
                'concepts': {
                    'basico_proporcional': round(propor),
                    'auxilio_transporte': round(aux),
                },
                'deducciones': {
                    'salud_4': salud,
                    'pension_4': pension,
                    'solidaridad_1': solidaridad
                },
                'totals': {
                    'devengados': devengados,
                    'deducciones': deducciones,
                    'neto': neto
                },
                'created_at': _now()
            }
            collection('nomina').insert_one(doc)
            created += 1
        flash(f'Generación completada. Registros creados: {created}', 'success')
        return redirect(url_for('nomina.list_runs', year=year, month=month))
    # GET
    today = datetime.today()
    return render_template('nomina_generar.html', conf=conf, default_year=today.year, default_month=today.month)


@nomina_bp.route('/liquidaciones')
@login_required
def list_runs():
    year = int(request.args.get('year') or 0)
    month = int(request.args.get('month') or 0)
    q = {}
    if year and month:
        q['period'] = int(f"{year:04d}{month:02d}")
    items = list(collection('nomina').find(q).sort([('period', -1), ('created_at', -1)]))
    return render_template('nomina_list.html', items=items)


@nomina_bp.route('/comprobante/<id>')
@login_required
def comprobante(id):
    doc = collection('nomina').find_one({'_id': ObjectId(id)})
    if not doc:
        flash('Comprobante no encontrado.', 'danger')
        return redirect(url_for('nomina.home'))
    return render_template('nomina_comprobante.html', doc=doc)


@nomina_bp.route('/export/csv')
@login_required
def export_csv():
    year = int(request.args.get('year') or 0)
    month = int(request.args.get('month') or 0)
    q = {}
    if year and month:
        q['period'] = int(f"{year:04d}{month:02d}")
    items = list(collection('nomina').find(q).sort([('period', -1), ('created_at', -1)]))
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(['period','employee','document_id','position','base_salary','basico','auxilio','salud','pension','solidaridad','devengados','deducciones','neto'])
    for it in items:
        emp = it.get('empleado', {})
        c = it.get('concepts', {})
        d = it.get('deducciones', {})
        t = it.get('totals', {})
        writer.writerow([
            it.get('period'), emp.get('name'), emp.get('document_id'), emp.get('position'), emp.get('base_salary'),
            c.get('basico_proporcional'), c.get('auxilio_transporte'),
            d.get('salud_4'), d.get('pension_4'), d.get('solidaridad_1'),
            t.get('devengados'), t.get('deducciones'), t.get('neto')
        ])
    output.seek(0)
    filename = f"nomina_{year}_{month}.csv" if (year and month) else 'nomina.csv'
    return send_file(output, mimetype='text/csv', as_attachment=True, download_name=filename)
