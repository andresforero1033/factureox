from flask import Blueprint, render_template

pages_bp = Blueprint('pages', __name__)


@pages_bp.route('/terminos')
def terms():
    return render_template('terminos.html')


@pages_bp.route('/privacidad')
def privacy():
    return render_template('privacidad.html')
