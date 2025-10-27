from flask import Blueprint, render_template, request, redirect, url_for, flash
from db import collection

contact_bp = Blueprint('contact', __name__)


@contact_bp.route('/contacto', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip().lower()
        subject = request.form.get('subject', '').strip()
        message = request.form.get('message', '').strip()
        from_index = request.form.get('from_index') == '1'

        errors = []
        if not name:
            errors.append('El nombre es obligatorio.')
        if not email or '@' not in email:
            errors.append('Ingresa un correo válido.')
        if not subject:
            errors.append('El asunto es obligatorio.')
        if not message or len(message) < 10:
            errors.append('El mensaje debe tener al menos 10 caracteres.')

        if errors:
            for e in errors:
                flash(e, 'warning')
            if from_index:
                return redirect(url_for('index') + '#contacto')
            return render_template('contact.html', form={
                'name': name, 'email': email, 'subject': subject, 'message': message
            })

        # Guardar en Mongo (colección messages)
        messages = collection('messages')
        messages.insert_one({
            'name': name,
            'email': email,
            'subject': subject,
            'message': message,
        })
        flash('Tu mensaje fue enviado. Te contactaremos pronto.', 'success')
        if from_index:
            return redirect(url_for('index') + '#contacto')
        return redirect(url_for('contact.contact'))

    return render_template('contact.html')
