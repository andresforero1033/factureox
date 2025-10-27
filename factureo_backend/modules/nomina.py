from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, send_file
from flask_login import login_required, current_user
from db import collection, ObjectId
from datetime import datetime
from io import StringIO, BytesIO
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
    owner_id = ObjectId(current_user.id)
    runs = list(collection('nomina').aggregate([
        { '$match': { 'owner_id': owner_id } },
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
    owner_id = ObjectId(current_user.id)
    empleados = list(collection('empleados').find({'owner_id': owner_id}).sort('name', 1))
    return render_template('nomina_empleados_list.html', empleados=empleados)


@nomina_bp.route('/empleados/nuevo', methods=['GET','POST'])
@login_required
def empleados_new():
    if request.method == 'POST':
        name = request.form.get('name','').strip()
        doc_id = request.form.get('document_id','').strip()
        position = request.form.get('position','').strip()
        email = (request.form.get('email') or '').strip().lower()
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
            'email': email or None,
            'base_salary': base_salary,
            'contract_type': contract_type,
            'start_date': start_date,
            'active': active,
            'eligible_transport': eligible_transport,
            'created_at': _now()
        }
        doc['owner_id'] = ObjectId(current_user.id)
        res = collection('empleados').insert_one(doc)
        flash('Empleado creado.', 'success')
        return redirect(url_for('nomina.empleados_list'))
    return render_template('nomina_empleados_form.html')


@nomina_bp.route('/empleados/editar/<id>', methods=['GET','POST'])
@login_required
def empleados_edit(id):
    empleados = collection('empleados')
    owner_id = ObjectId(current_user.id)
    emp = empleados.find_one({'_id': ObjectId(id), 'owner_id': owner_id})
    if not emp:
        flash('Empleado no encontrado', 'danger')
        return redirect(url_for('nomina.empleados_list'))
    if request.method == 'POST':
        name = request.form.get('name','').strip()
        doc_id = request.form.get('document_id','').strip()
        position = request.form.get('position','').strip()
        email = (request.form.get('email') or '').strip().lower()
        base_salary = int(request.form.get('base_salary','0') or 0)
        contract_type = request.form.get('contract_type','indefinido')
        start_date = request.form.get('start_date')
        active = request.form.get('active') == 'on'
        eligible_transport = request.form.get('eligible_transport') == 'on'
        if not name or not doc_id or base_salary <= 0:
            flash('Nombre, documento y salario base son obligatorios.', 'warning')
            return render_template('nomina_empleados_form.html', emp=emp)
        empleados.update_one({'_id': emp['_id'], 'owner_id': owner_id}, {'$set': {
            'name': name,
            'document_id': doc_id,
            'position': position,
            'email': email or None,
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


@nomina_bp.route('/empleados/eliminar/<id>', methods=['POST'])
@login_required
def empleados_delete(id):
    empleados = collection('empleados')
    owner_id = ObjectId(current_user.id)
    try:
        emp_id = ObjectId(id)
    except Exception:
        flash('Identificador inválido.', 'danger')
        return redirect(url_for('nomina.empleados_list'))
    emp = empleados.find_one({'_id': emp_id, 'owner_id': owner_id})
    if not emp:
        flash('Empleado no encontrado.', 'warning')
        return redirect(url_for('nomina.empleados_list'))
    cascade = (request.form.get('cascade') == '1')
    runs_count = collection('nomina').count_documents({'empleado_id': emp_id, 'owner_id': owner_id})
    if runs_count and not cascade:
        flash('No se puede eliminar: el empleado tiene liquidaciones asociadas. Usa "Eliminar todo" si deseas borrar también sus liquidaciones.', 'warning')
        return redirect(url_for('nomina.empleados_list'))
    if cascade and runs_count:
        collection('nomina').delete_many({'empleado_id': emp_id, 'owner_id': owner_id})
    empleados.delete_one({'_id': emp_id, 'owner_id': owner_id})
    flash('Empleado eliminado correctamente.' + (' (con liquidaciones)' if cascade else ''), 'success')
    return redirect(url_for('nomina.empleados_list'))


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
        owner_id = ObjectId(current_user.id)
        empleados = list(collection('empleados').find({'active': True, 'owner_id': owner_id}))
        if not empleados:
            flash('No hay empleados activos.', 'info')
            return render_template('nomina_generar.html', conf=conf)
        created = 0
        for emp in empleados:
            # Evitar duplicado del periodo por empleado
            exists = collection('nomina').find_one({'period': period, 'empleado_id': emp['_id'], 'owner_id': owner_id})
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
                'created_at': _now(),
                'owner_id': owner_id
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
    q['owner_id'] = ObjectId(current_user.id)
    items = list(collection('nomina').find(q).sort([('period', -1), ('created_at', -1)]))
    return render_template('nomina_list.html', items=items)


@nomina_bp.route('/comprobante/<id>')
@login_required
def comprobante(id):
    doc = collection('nomina').find_one({'_id': ObjectId(id), 'owner_id': ObjectId(current_user.id)})
    if not doc:
        flash('Comprobante no encontrado.', 'danger')
        return redirect(url_for('nomina.home'))
    return render_template('nomina_comprobante.html', doc=doc)


def _generate_payslip_pdf(doc):
    # Importar de forma diferida para no romper el arranque si falta la dependencia
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfgen import canvas
    from reportlab.lib.units import mm
    from reportlab.lib import colors

    buf = BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)
    width, height = A4

    def line(y):
        c.setStrokeColor(colors.grey)
        c.line(20*mm, y, width-20*mm, y)

    def money(n):
        try:
            return f"${n:,.0f}".replace(',', '.')
        except Exception:
            return str(n)

    y = height - 30*mm
    c.setFont("Helvetica-Bold", 14)
    c.drawString(20*mm, y, "Comprobante de nómina")
    y -= 10*mm
    c.setFont("Helvetica", 10)
    c.drawString(20*mm, y, f"Año: {doc.get('year')}  Mes: {doc.get('month')}  Días: {doc.get('days')}")
    y -= 6*mm
    c.drawString(20*mm, y, f"Generado: {doc.get('created_at')}")
    y -= 10*mm
    line(y)
    y -= 8*mm

    emp = doc.get('empleado', {})
    c.setFont("Helvetica-Bold", 11)
    c.drawString(20*mm, y, "Empleado")
    y -= 6*mm
    c.setFont("Helvetica", 10)
    c.drawString(20*mm, y, f"Nombre: {emp.get('name')}")
    y -= 6*mm
    c.drawString(20*mm, y, f"Documento: {emp.get('document_id')}")
    y -= 6*mm
    c.drawString(20*mm, y, f"Cargo: {emp.get('position') or '-'}")
    y -= 6*mm
    c.drawString(20*mm, y, f"Salario base: {money(emp.get('base_salary'))}")
    y -= 10*mm
    line(y)
    y -= 8*mm

    c.setFont("Helvetica-Bold", 11)
    c.drawString(20*mm, y, "Devengados")
    y -= 6*mm
    c.setFont("Helvetica", 10)
    concepts = doc.get('concepts', {})
    c.drawString(25*mm, y, f"Básico proporcional: {money(concepts.get('basico_proporcional', 0))}")
    y -= 6*mm
    c.drawString(25*mm, y, f"Auxilio de transporte: {money(concepts.get('auxilio_transporte', 0))}")
    y -= 10*mm

    c.setFont("Helvetica-Bold", 11)
    c.drawString(110*mm, y+16*mm, "Deducciones")
    c.setFont("Helvetica", 10)
    ded = doc.get('deducciones', {})
    c.drawString(115*mm, y+10*mm, f"Salud (4%): {money(ded.get('salud_4', 0))}")
    c.drawString(115*mm, y+4*mm, f"Pensión (4%): {money(ded.get('pension_4', 0))}")
    c.drawString(115*mm, y-2*mm, f"Fondo solidaridad (1%): {money(ded.get('solidaridad_1', 0))}")
    y -= 12*mm
    line(y)
    y -= 8*mm

    t = doc.get('totals', {})
    c.setFont("Helvetica", 11)
    c.drawString(20*mm, y, f"Devengados: {money(t.get('devengados', 0))}")
    y -= 6*mm
    c.drawString(20*mm, y, f"Deducciones: {money(t.get('deducciones', 0))}")
    y -= 8*mm
    c.setFont("Helvetica-Bold", 12)
    c.drawString(20*mm, y, f"Neto a pagar: {money(t.get('neto', 0))}")

    c.showPage()
    c.save()
    buf.seek(0)
    return buf


@nomina_bp.route('/comprobante/<id>/pdf')
@login_required
def comprobante_pdf(id):
    doc = collection('nomina').find_one({'_id': ObjectId(id), 'owner_id': ObjectId(current_user.id)})
    if not doc:
        flash('Comprobante no encontrado.', 'danger')
        return redirect(url_for('nomina.home'))
    try:
        pdf = _generate_payslip_pdf(doc)
    except Exception as e:
        current_app.logger.exception('Error generando PDF de nómina')
        flash('No se pudo generar el PDF del comprobante.', 'danger')
        return redirect(url_for('nomina.comprobante', id=id))
    filename = f"comprobante_nomina_{doc.get('year')}_{doc.get('month')}_{str(doc.get('_id'))[:6]}.pdf"
    return send_file(pdf, mimetype='application/pdf', as_attachment=True, download_name=filename)


def _send_email_with_attachment(to_email: str, subject: str, body_text: str, filename: str, file_bytes: bytes):
    import smtplib
    from email.message import EmailMessage

    cfg = current_app.config
    smtp_host = cfg.get('MAIL_SERVER')
    smtp_port = int(cfg.get('MAIL_PORT', 587))
    use_tls = bool(cfg.get('MAIL_USE_TLS', True))
    username = cfg.get('MAIL_USERNAME')
    password = cfg.get('MAIL_PASSWORD')
    sender = cfg.get('MAIL_SENDER') or username

    if not smtp_host or not sender:
        raise RuntimeError('SMTP no configurado (MAIL_SERVER/MAIL_SENDER).')

    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = to_email
    msg.set_content(body_text)
    msg.add_attachment(file_bytes, maintype='application', subtype='pdf', filename=filename)

    with smtplib.SMTP(smtp_host, smtp_port, timeout=20) as s:
        if use_tls:
            s.starttls()
        if username and password:
            s.login(username, password)
        s.send_message(msg)


@nomina_bp.route('/comprobante/<id>/enviar', methods=['POST'])
@login_required
def comprobante_enviar(id):
    doc = collection('nomina').find_one({'_id': ObjectId(id), 'owner_id': ObjectId(current_user.id)})
    if not doc:
        flash('Comprobante no encontrado.', 'danger')
        return redirect(url_for('nomina.home'))

    # Buscar el correo del empleado en su registro maestro
    emp_id = doc.get('empleado_id')
    emp = None
    if emp_id:
        emp = collection('empleados').find_one({'_id': emp_id, 'owner_id': ObjectId(current_user.id)})
    to_email = (emp or {}).get('email')
    if not to_email:
        flash('El empleado no tiene un correo registrado. Actualiza su ficha para poder enviar el comprobante.', 'warning')
        return redirect(url_for('nomina.comprobante', id=id))

    # Validar configuración SMTP antes de generar el PDF
    cfg = current_app.config
    missing = []
    if not cfg.get('MAIL_SERVER'):
        missing.append('MAIL_SERVER')
    if not (cfg.get('MAIL_SENDER') or cfg.get('MAIL_USERNAME')):
        missing.append('MAIL_SENDER o MAIL_USERNAME')
    if missing:
        flash('SMTP no configurado: faltan ' + ', '.join(missing) + '. Configura las variables en .env.', 'warning')
        return redirect(url_for('nomina.comprobante', id=id))

    try:
        pdf_buf = _generate_payslip_pdf(doc)
        pdf_bytes = pdf_buf.read()
        filename = f"comprobante_nomina_{doc.get('year')}_{doc.get('month')}_{str(doc.get('_id'))[:6]}.pdf"
        subject = f"Comprobante de nómina - {doc.get('year')}-{doc.get('month'):02d}"
        body = (
            f"Hola {doc.get('empleado', {}).get('name')},\n\n"
            f"Adjuntamos tu comprobante de nómina correspondiente al periodo {doc.get('year')}-{doc.get('month'):02d}.\n\n"
            f"Este es un mensaje automático de Factureo."
        )
        _send_email_with_attachment(to_email, subject, body, filename, pdf_bytes)
    except Exception as e:
        import smtplib
        current_app.logger.exception('Error enviando comprobante de nómina por correo')
        if isinstance(e, smtplib.SMTPAuthenticationError):
            flash('Error SMTP: autenticación fallida. Verifica MAIL_USERNAME y MAIL_PASSWORD.', 'danger')
        elif isinstance(e, (ConnectionRefusedError, OSError)):
            flash('Error SMTP: no se pudo conectar al servidor. Verifica MAIL_SERVER y MAIL_PORT, y si requiere TLS.', 'danger')
        elif isinstance(e, RuntimeError):
            flash(str(e), 'danger')
        else:
            # En modo DEBUG, muestra el detalle para facilitar soporte
            if cfg.get('DEBUG'):
                flash(f'No se pudo enviar el comprobante: {e}', 'danger')
            else:
                flash('No se pudo enviar el comprobante por correo.', 'danger')
        return redirect(url_for('nomina.comprobante', id=id))

    flash('Comprobante enviado por correo correctamente.', 'success')
    return redirect(url_for('nomina.comprobante', id=id))


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
