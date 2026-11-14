"""Registro de blueprints de la API."""

from ..auth import proteger_blueprint
from .carreras import carreras_bp
from .cursos import cursos_bp
from .estudiantes import estudiantes_bp
from .health import health_bp
from .inscripciones import inscripciones_bp
from .ui import ui_bp

# Los recursos académicos exigen sesión y rol admin para escribir.
for _bp in (carreras_bp, cursos_bp, estudiantes_bp, inscripciones_bp):
    proteger_blueprint(_bp)


def register_blueprints(app) -> None:
    app.register_blueprint(ui_bp)
    app.register_blueprint(health_bp)
    app.register_blueprint(carreras_bp)
    app.register_blueprint(cursos_bp)
    app.register_blueprint(estudiantes_bp)
    app.register_blueprint(inscripciones_bp)
