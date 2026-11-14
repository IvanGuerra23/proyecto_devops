"""Fábrica de la aplicación Flask."""

import os

import click
from flask import Flask

from .auth import init_auth
from .extensions import db, migrate


def create_app(config_object=None) -> Flask:
    app = Flask(__name__, instance_relative_config=True)

    from config import Config

    app.config.from_object(config_object or Config)
    app.json.sort_keys = False
    os.makedirs(app.instance_path, exist_ok=True)

    db.init_app(app)
    migrate.init_app(app, db)

    from .observability import init_observability
    from .routes import register_blueprints

    init_auth(app)
    init_observability(app)
    register_blueprints(app)

    @app.cli.command("init-db")
    def init_db_command() -> None:
        """Aplica migraciones y carga datos de ejemplo (idempotente)."""
        from .db_migrations import run_migrations
        from .seed import ensure_default_users, load_seed_data

        run_migrations(app)
        with app.app_context():
            load_seed_data()
            ensure_default_users()
        click.echo("Esquema migrado, datos y usuarios listos.")

    @app.cli.command("seed")
    def seed_command() -> None:
        """Carga datos de ejemplo y usuarios demo si no existen."""
        from .seed import ensure_default_users, load_seed_data

        with app.app_context():
            load_seed_data()
            ensure_default_users()
        click.echo("Datos de ejemplo y usuarios verificados.")

    return app
