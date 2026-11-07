"""Inicialización del esquema y de los datos de ejemplo."""

from . import models  # noqa: F401  (registra los modelos en SQLAlchemy)
from .extensions import db
from .seed import load_seed_data


def init_database(app) -> None:
    """Crea las tablas y, si corresponde, carga los datos de ejemplo."""
    with app.app_context():
        db.create_all()
        if app.config.get("SEED_DATA", False):
            load_seed_data()
