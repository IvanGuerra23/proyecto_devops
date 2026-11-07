"""Registro de blueprints de la API."""

from .carreras import carreras_bp
from .cursos import cursos_bp
from .estudiantes import estudiantes_bp
from .health import health_bp
from .inscripciones import inscripciones_bp


def register_blueprints(app) -> None:
    app.register_blueprint(health_bp)
    app.register_blueprint(carreras_bp)
    app.register_blueprint(cursos_bp)
    app.register_blueprint(estudiantes_bp)
    app.register_blueprint(inscripciones_bp)
