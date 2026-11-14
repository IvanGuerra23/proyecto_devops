"""Aplicación de migraciones Alembic con compatibilidad hacia atrás."""

from sqlalchemy import inspect

from .extensions import db


def run_migrations(app) -> None:
    """Aplica las migraciones pendientes.

    Las bases creadas en avances anteriores (con ``create_all``) no tienen
    tabla ``alembic_version``. En ese caso se marca la revisión actual antes
    de continuar, evitando intentar crear tablas que ya existen.
    """
    from flask_migrate import stamp, upgrade

    with app.app_context():
        tablas = set(inspect(db.engine).get_table_names())
        if tablas and "alembic_version" not in tablas:
            stamp()
        upgrade()


def main() -> int:
    from . import create_app

    app = create_app()
    run_migrations(app)
    print("[migrate] Migraciones aplicadas correctamente.", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
