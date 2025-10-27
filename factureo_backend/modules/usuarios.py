from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
from datetime import datetime
from db import collection, ObjectId

auth_bp = Blueprint('auth', __name__)


class User(UserMixin):
    def __init__(self, _id, name, email, username, role=None, company=None, avatar_url=None, theme=None):
        self.id = str(_id)
        self.name = name
        self.email = email
        self.username = username
        self.role = role or 'user'
        self.company = company
        self.avatar_url = avatar_url
        self.theme = theme or 'dark'

    @staticmethod
    def from_doc(doc):
        return User(
            doc.get('_id'),
            doc.get('name'),
            doc.get('email'),
            doc.get('username'),
            doc.get('role'),
            doc.get('company'),
            doc.get('avatar_url'),
            doc.get('theme'),
        )

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
            return _redirect_by_role(user_doc.get('role'))
        flash('Credenciales inválidas', 'danger')
    return render_template('login.html')


def _redirect_by_role(role: str | None):
    role = (role or 'user').lower()
    # Mapeo básico; ajustar según dashboards específicos si existen
    if role in ('admin', 'owner'):
        return redirect(url_for('auth.dashboard'))
    if role in ('ventas', 'seller', 'sales'):
        try:
            return redirect(url_for('ventas.list_sales'))
        except Exception:
            return redirect(url_for('auth.dashboard'))
    if role in ('inventario', 'inventory'):
        try:
            return redirect(url_for('inventario.list_products'))
        except Exception:
            return redirect(url_for('auth.dashboard'))
    if role in ('clientes', 'customers', 'support'):
        try:
            return redirect(url_for('clientes.list_clients'))
        except Exception:
            return redirect(url_for('auth.dashboard'))
    return redirect(url_for('auth.dashboard'))


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip().lower()
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        # Validaciones básicas
        if not name or not email or not username or not password:
            flash('Todos los campos son obligatorios', 'warning')
            return render_template('register.html')
        if len(password) < 6:
            flash('La contraseña debe tener al menos 6 caracteres', 'warning')
            return render_template('register.html')
        if collection('users').find_one({'email': email}):
            flash('El email ya está registrado', 'warning')
            return render_template('register.html')

        hashed = generate_password_hash(password)
        users = collection('users')
        doc = {
            'name': name,
            'email': email,
            'username': username,
            'password': hashed,
            'role': 'user',
            'company': None,
            'avatar_url': None,
            'theme': 'dark'
        }
        res = users.insert_one(doc)
        doc['_id'] = res.inserted_id
        # Autologin post-registro
        login_user(User.from_doc(doc))
        flash('Registro exitoso. ¡Bienvenido a Factureo!', 'success')
        return redirect(url_for('auth.dashboard'))

    return render_template('register.html')


@auth_bp.route('/dashboard')
@login_required
def dashboard():
    # Métricas resumidas para las tarjetas
    try:
        products_count = collection('productos').count_documents({})
    except Exception:
        products_count = 0
    try:
        clients_count = collection('clientes').count_documents({})
    except Exception:
        clients_count = 0
    try:
        sales_count = collection('ventas').count_documents({})
    except Exception:
        sales_count = 0

    metrics = {
        'products': products_count,
        'clients': clients_count,
        'sales': sales_count,
    }
    return render_template('dashboard.html', user=current_user, metrics=metrics)


def _allowed_file(filename: str) -> bool:
    allowed = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed


@auth_bp.route('/perfil', methods=['GET', 'POST'])
@login_required
def profile():
    users = collection('users')
    user_doc = users.find_one({'_id': ObjectId(current_user.id)})
    if not user_doc:
        flash('Usuario no encontrado.', 'danger')
        return redirect(url_for('auth.dashboard'))

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip().lower()
        company = request.form.get('company', '').strip() or None
        theme = request.form.get('theme', '').strip() or user_doc.get('theme') or 'dark'

        # Validaciones básicas
        if not name or not username or not email:
            flash('Nombre, usuario y correo son obligatorios.', 'warning')
            return render_template('profile.html', user=current_user, doc=user_doc)

        # Duplicados de email/username
        if email != user_doc.get('email') and users.find_one({'email': email, '_id': {'$ne': user_doc['_id']}}):
            flash('El correo ya está en uso.', 'warning')
            return render_template('profile.html', user=current_user, doc=user_doc)
        if username != user_doc.get('username') and users.find_one({'username': username, '_id': {'$ne': user_doc['_id']}}):
            flash('El nombre de usuario ya está en uso.', 'warning')
            return render_template('profile.html', user=current_user, doc=user_doc)

        update_fields = {
            'name': name,
            'username': username,
            'email': email,
            'company': company,
            'theme': theme,
        }

        # Cambio de contraseña (opcional)
        current_password = request.form.get('current_password') or ''
        new_password = request.form.get('new_password') or ''
        confirm_password = request.form.get('confirm_password') or ''
        if new_password or confirm_password:
            if len(new_password) < 6:
                flash('La nueva contraseña debe tener al menos 6 caracteres.', 'warning')
                return render_template('profile.html', user=current_user, doc=user_doc)
            if new_password != confirm_password:
                flash('La confirmación de contraseña no coincide.', 'warning')
                return render_template('profile.html', user=current_user, doc=user_doc)
            # Verificar contraseña actual salvo usuarios OAuth sin contraseña local
            stored_hash = user_doc.get('password')
            if stored_hash:
                if not current_password or not check_password_hash(stored_hash, current_password):
                    flash('La contraseña actual es incorrecta.', 'danger')
                    return render_template('profile.html', user=current_user, doc=user_doc)
            update_fields['password'] = generate_password_hash(new_password)

        # Avatar (opcional)
        file = request.files.get('avatar')
        if file and file.filename:
            if not _allowed_file(file.filename):
                flash('Formato de imagen no permitido. Usa png, jpg, jpeg, gif o webp.', 'warning')
                return render_template('profile.html', user=current_user, doc=user_doc)
            filename = secure_filename(file.filename)
            ext = filename.rsplit('.', 1)[1].lower()
            # Nombre determinístico por usuario + timestamp para cache busting
            ts = datetime.utcnow().strftime('%Y%m%d%H%M%S')
            new_name = f"avatar_{current_user.id}_{ts}.{ext}"
            avatars_dir = os.path.join(current_app.root_path, 'static', 'img', 'avatars')
            os.makedirs(avatars_dir, exist_ok=True)
            save_path = os.path.join(avatars_dir, new_name)
            file.save(save_path)
            update_fields['avatar_url'] = f"img/avatars/{new_name}"

        # Persistir cambios
        users.update_one({'_id': user_doc['_id']}, {'$set': update_fields})
        # Refrescar current_user (mínimo los campos visibles)
        for k in ['name', 'username', 'email', 'company', 'theme', 'avatar_url']:
            if hasattr(current_user, k) and k in update_fields:
                setattr(current_user, k, update_fields[k])
        flash('Perfil actualizado correctamente.', 'success')
        return redirect(url_for('auth.profile'))

    # GET
    return render_template('profile.html', user=current_user, doc=user_doc)


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Sesión finalizada', 'info')
    return redirect(url_for('auth.login'))


# --------- OAuth: Google ---------
@auth_bp.route('/login/google')
def login_google():
    oauth = getattr(current_app, 'oauth', None)
    if not oauth or 'google' not in getattr(oauth, 'clients', {}):
        flash('Inicio con Google no está configurado.', 'warning')
        return redirect(url_for('auth.login'))
    redirect_uri = url_for('auth.google_callback', _external=True)
    return oauth.google.authorize_redirect(redirect_uri)


@auth_bp.route('/auth/google/callback')
def google_callback():
    oauth = getattr(current_app, 'oauth', None)
    if not oauth or 'google' not in getattr(oauth, 'clients', {}):
        flash('Google OAuth no disponible.', 'warning')
        return redirect(url_for('auth.login'))
    token = oauth.google.authorize_access_token()
    # Intentar obtener claims vía OIDC
    userinfo = None
    try:
        userinfo = oauth.google.parse_id_token(token)
    except Exception:
        pass
    if not userinfo:
        try:
            resp = oauth.google.get('userinfo')
            userinfo = resp.json()
        except Exception:
            userinfo = {}
    email = (userinfo or {}).get('email')
    name = (userinfo or {}).get('name') or ''
    if not email:
        flash('No pudimos obtener tu email desde Google.', 'danger')
        return redirect(url_for('auth.login'))
    # Buscar o crear usuario
    users = collection('users')
    user_doc = users.find_one({'email': email})
    if not user_doc:
        user_doc = {
            'name': name or email.split('@')[0],
            'email': email,
            'username': email.split('@')[0],
            'role': 'user',
            'oauth_provider': 'google'
        }
        res = users.insert_one(user_doc)
        user_doc['_id'] = res.inserted_id
    login_user(User.from_doc(user_doc))
    flash('Inicio de sesión con Google exitoso', 'success')
    return _redirect_by_role(user_doc.get('role'))


# --------- OAuth: Microsoft ---------
@auth_bp.route('/login/microsoft')
def login_microsoft():
    oauth = getattr(current_app, 'oauth', None)
    if not oauth or 'microsoft' not in getattr(oauth, 'clients', {}):
        flash('Inicio con Microsoft no está configurado.', 'warning')
        return redirect(url_for('auth.login'))
    redirect_uri = url_for('auth.microsoft_callback', _external=True)
    return oauth.microsoft.authorize_redirect(redirect_uri)


@auth_bp.route('/auth/microsoft/callback')
def microsoft_callback():
    oauth = getattr(current_app, 'oauth', None)
    if not oauth or 'microsoft' not in getattr(oauth, 'clients', {}):
        flash('Microsoft OAuth no disponible.', 'warning')
        return redirect(url_for('auth.login'))
    token = oauth.microsoft.authorize_access_token()
    userinfo = None
    try:
        userinfo = oauth.microsoft.parse_id_token(token)
    except Exception:
        pass
    if not userinfo:
        # Microsoft Graph user endpoint (requiere permisos); omitimos por simplicidad
        userinfo = {}
    email = userinfo.get('email') or userinfo.get('preferred_username')
    name = userinfo.get('name') or ''
    if not email:
        flash('No pudimos obtener tu email desde Microsoft.', 'danger')
        return redirect(url_for('auth.login'))
    users = collection('users')
    user_doc = users.find_one({'email': email})
    if not user_doc:
        user_doc = {
            'name': name or email.split('@')[0],
            'email': email,
            'username': email.split('@')[0],
            'role': 'user',
            'oauth_provider': 'microsoft'
        }
        res = users.insert_one(user_doc)
        user_doc['_id'] = res.inserted_id
    login_user(User.from_doc(user_doc))
    flash('Inicio de sesión con Microsoft exitoso', 'success')
    return _redirect_by_role(user_doc.get('role'))


# --------- Recuperar contraseña ---------
@auth_bp.route('/forgot', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        if not email:
            flash('Ingresa tu correo.', 'warning')
            return render_template('forgot_password.html')
        # Por seguridad, no revelamos si el correo existe
        flash('Si el correo existe, te enviaremos instrucciones para recuperar tu contraseña.', 'info')
        return redirect(url_for('auth.login'))
    return render_template('forgot_password.html')
