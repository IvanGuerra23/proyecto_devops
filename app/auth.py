"""Autenticación por sesión y control de roles."""

from urllib.parse import urlparse

from flask import (
    Blueprint,
    jsonify,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_login import (
    LoginManager,
    current_user,
    login_required,
    login_user,
    logout_user,
)
from sqlalchemy import select

from .extensions import db
from .models import Usuario
from .utils import error

login_manager = LoginManager()
auth_bp = Blueprint("auth", __name__)

SAFE_METHODS = {"GET", "HEAD", "OPTIONS"}


def _quiere_json() -> bool:
    """Determina si la petición espera una respuesta JSON."""
    return request.is_json or request.accept_mimetypes.best == "application/json"


def _destino_seguro(candidato: str | None) -> str:
    """Evita redirecciones abiertas tras el login."""
    if not candidato:
        return url_for("ui.index")

    parsed = urlparse(candidato)
    if parsed.scheme or parsed.netloc or not candidato.startswith("/"):
        return url_for("ui.index")
    if candidato.startswith("//"):
        return url_for("ui.index")
    return candidato


@login_manager.user_loader
def _cargar_usuario(user_id: str):
    try:
        return db.session.get(Usuario, int(user_id))
    except (TypeError, ValueError):
        return None


@login_manager.unauthorized_handler
def _no_autorizado():
    if request.path == "/" and request.method == "GET":
        return redirect(url_for("auth.login", next=request.full_path))
    return jsonify({"error": "Autenticación requerida"}), 401


def init_auth(app) -> None:
    """Inicializa Flask-Login y registra el blueprint de autenticación."""
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"
    login_manager.login_message = "Inicia sesión para continuar."
    app.register_blueprint(auth_bp)


def proteger_blueprint(bp) -> None:
    """Exige sesión para un blueprint y rol admin para las escrituras."""
    @bp.before_request
    @login_required
    def _exigir_sesion():
        return None

    @bp.before_request
    def _exigir_admin():
        if request.method not in SAFE_METHODS and not current_user.is_admin:
            return error("Se requiere rol admin para modificar datos", 403)
        return None


@auth_bp.get("/login")
def login_form():
    if current_user.is_authenticated:
        return redirect(url_for("ui.index"))
    return render_template("login.html")


@auth_bp.post("/login")
def login():
    data = request.get_json(silent=True) or request.form
    email = str(data.get("email", "")).strip().lower()
    password = str(data.get("password", ""))

    if not email or not password:
        if _quiere_json():
            return error("Email y contraseña son obligatorios")
        return (
            render_template(
                "login.html",
                error="Completa el email y la contraseña.",
                email=email,
            ),
            400,
        )

    usuario = db.session.scalar(select(Usuario).where(Usuario.email == email))

    if usuario is None or not usuario.activo or not usuario.check_password(password):
        if _quiere_json():
            return error("Credenciales inválidas", 401)
        return (
            render_template(
                "login.html",
                error="Credenciales inválidas.",
                email=email,
            ),
            401,
        )

    login_user(usuario)
    destino = _destino_seguro(request.args.get("next") or data.get("next"))

    if _quiere_json():
        return jsonify({"usuario": usuario.to_dict()}), 200
    return redirect(destino)


@auth_bp.post("/logout")
@login_required
def logout():
    logout_user()
    if _quiere_json():
        return jsonify({"status": "ok"}), 200
    return redirect(url_for("auth.login"))
