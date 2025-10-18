from flask import Flask, render_template, redirect, url_for
from flask_login import LoginManager, current_user
from config import config
from modules.usuarios import auth_bp, User
from modules.inventario import inventario_bp
from modules.clientes import clientes_bp
from modules.ventas import ventas_bp


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
    app.register_blueprint(inventario_bp, url_prefix="/inventario")
    app.register_blueprint(clientes_bp, url_prefix="/clientes")
    app.register_blueprint(ventas_bp, url_prefix="/ventas")

    @app.route("/")
    def index():
        if current_user.is_authenticated:
            return redirect(url_for("auth.dashboard"))
        return render_template("index.html")

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host="127.0.0.1", port=5000, debug=config.DEBUG)
