"""Configuración central de la aplicación basada en variables de entorno."""

import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
INSTANCE_DIR = os.path.join(BASE_DIR, "instance")


def normalize_database_url(url: str) -> str:
    """Fuerza el driver PyMySQL cuando se usa el esquema corto ``mysql://``."""
    if url.startswith("mysql://"):
        return "mysql+pymysql://" + url.removeprefix("mysql://")
    return url


class Config:
    """Configuración por defecto (Docker Compose pasa DATABASE_URL)."""

    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-cambiar-en-produccion")
    SQLALCHEMY_DATABASE_URI = normalize_database_url(
        os.getenv(
            "DATABASE_URL",
            f"sqlite:///{os.path.join(INSTANCE_DIR, 'estudiantes.db')}",
        )
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        "pool_recycle": 280,
    }
    # Carga datos de ejemplo solo cuando las tablas están vacías.
    SEED_DATA = os.getenv("SEED_DATA", "true").lower() in {"1", "true", "yes"}
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()


class TestingConfig(Config):
    """Configuración para pruebas: SQLite en memoria y sin datos de ejemplo."""

    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    SQLALCHEMY_ENGINE_OPTIONS = {}
    SEED_DATA = False
