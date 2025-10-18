from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from db import collection, ObjectId

auth_bp = Blueprint('auth', __name__)


class User(UserMixin):
    def __init__(self, _id, name, email, username):
        self.id = str(_id)
        self.name = name
        self.email = email
        self.username = username

    @staticmethod
    def from_doc(doc):
        return User(doc.get('_id'), doc.get('name'), doc.get('email'), doc.get('username'))

    @staticmethod
    def get_by_id(user_id):
        doc = collection('users').find_one({'_id': ObjectId(user_id)})
        return User.from_doc(doc) if doc else None


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        user_doc = collection('users').find_one({'email': email})
        if user_doc and check_password_hash(user_doc.get('password', ''), password):
            login_user(User.from_doc(user_doc))
            flash('Inicio de sesión exitoso', 'success')
            return redirect(url_for('auth.dashboard'))
        flash('Credenciales inválidas', 'danger')
    return render_template('login.html')


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip().lower()
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        if not name or not email or not username or not password:
            flash('Todos los campos son obligatorios', 'warning')
            return render_template('register.html')

        if collection('users').find_one({'email': email}):
            flash('El email ya está registrado', 'warning')
            return render_template('register.html')

        hashed = generate_password_hash(password)
        res = collection('users').insert_one({
            'name': name,
            'email': email,
            'username': username,
            'password': hashed
        })
        flash('Registro exitoso, ahora puedes iniciar sesión', 'success')
        return redirect(url_for('auth.login'))

    return render_template('register.html')


@auth_bp.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', user=current_user)


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Sesión finalizada', 'info')
    return redirect(url_for('auth.login'))
