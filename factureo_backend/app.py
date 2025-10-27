from flask import Flask, render_template, redirect, url_for
from flask_login import LoginManager, current_user
from config import config
from modules.usuarios import auth_bp, User
from modules.contact import contact_bp
from modules.inventario import inventario_bp
from modules.clientes import clientes_bp
from modules.ventas import ventas_bp
from modules.noticias import news_bp
from modules.nomina import nomina_bp
from modules.pages import pages_bp
from db import collection


def create_app():
    app = Flask(__name__, template_folder="templates", static_folder="static")
    app.config.from_object(config)

    login_manager = LoginManager(app)
    login_manager.login_view = "auth.login"

    @login_manager.user_loader
    def load_user(user_id):
        return User.get_by_id(user_id)

    # Blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(contact_bp)
    app.register_blueprint(inventario_bp, url_prefix="/inventario")
    app.register_blueprint(clientes_bp, url_prefix="/clientes")
    app.register_blueprint(ventas_bp, url_prefix="/ventas")
    app.register_blueprint(news_bp)
    app.register_blueprint(nomina_bp, url_prefix="/nomina")
    app.register_blueprint(pages_bp)

    # OAuth (opcional; solo si hay credenciales)
    try:
        from authlib.integrations.flask_client import OAuth  # type: ignore
        oauth = OAuth(app)
        app.oauth = oauth
        if config.GOOGLE_CLIENT_ID and config.GOOGLE_CLIENT_SECRET:
            oauth.register(
                name="google",
                client_id=config.GOOGLE_CLIENT_ID,
                client_secret=config.GOOGLE_CLIENT_SECRET,
                server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
                client_kwargs={"scope": "openid email profile"},
            )
        if config.MICROSOFT_CLIENT_ID and config.MICROSOFT_CLIENT_SECRET:
            authority = f"https://login.microsoftonline.com/{config.MS_TENANT}"
            oauth.register(
                name="microsoft",
                client_id=config.MICROSOFT_CLIENT_ID,
                client_secret=config.MICROSOFT_CLIENT_SECRET,
                server_metadata_url=f"{authority}/v2.0/.well-known/openid-configuration",
                client_kwargs={"scope": "openid email profile offline_access"},
            )
    except Exception:
        # Authlib no instalado o error de configuración: OAuth deshabilitado
        pass

    @app.route("/")
    def index():
        if current_user.is_authenticated:
            return redirect(url_for("auth.dashboard"))
        # Últimas noticias publicadas para la sección del index
        try:
            items = list(collection('news').find({'published': True}).sort('created_at', -1).limit(6))
            news = []
            for it in items:
                news.append({
                    'id': str(it.get('_id')),
                    'title': it.get('title'),
                    'summary': it.get('summary'),
                    'author': it.get('author') or 'Equipo Factureo',
                    'created_at': it.get('created_at'),
                    'image_url': it.get('image_url') or None,
                })
        except Exception:
            news = []
        return render_template("index.html", news_list=news)

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host="127.0.0.1", port=5000, debug=config.DEBUG)
