"""Interfaz gráfica servida por Flask."""

from flask import Blueprint, render_template
from flask_login import current_user, login_required

ui_bp = Blueprint("ui", __name__)


@ui_bp.get("/")
@login_required
def index():
    return render_template("index.html", puede_escribir=current_user.is_admin)
