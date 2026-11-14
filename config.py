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

    # Cuentas de demostración creadas al arrancar si no existen.
    SEED_USERS = os.getenv("SEED_USERS", "true").lower() in {"1", "true", "yes"}
    SEED_ADMIN_EMAIL = os.getenv("SEED_ADMIN_EMAIL", "admin@example.com")
    SEED_ADMIN_PASSWORD = os.getenv("SEED_ADMIN_PASSWORD", "admin123")
    SEED_VIEWER_EMAIL = os.getenv("SEED_VIEWER_EMAIL", "lector@example.com")
    SEED_VIEWER_PASSWORD = os.getenv("SEED_VIEWER_PASSWORD", "lector123")

    # Sesiones: cookies solo HTTP y SameSite; Secure se activa en HTTPS.
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = os.getenv("SESSION_COOKIE_SECURE", "false").lower() in {
        "1",
        "true",
        "yes",
    }


class TestingConfig(Config):
    """Configuración para pruebas: SQLite en memoria y sin datos de ejemplo."""

    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    SQLALCHEMY_ENGINE_OPTIONS = {}
    SEED_DATA = False
