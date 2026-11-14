"""Fábrica de la aplicación Flask."""

import os

import click
from flask import Flask

from .extensions import db


def create_app(config_object=None) -> Flask:
    app = Flask(__name__, instance_relative_config=True)

    from config import Config

    app.config.from_object(config_object or Config)
    app.json.sort_keys = False
    os.makedirs(app.instance_path, exist_ok=True)

    db.init_app(app)

    from .db_init import init_database
    from .routes import register_blueprints

    register_blueprints(app)

    @app.cli.command("init-db")
    def init_db_command() -> None:
        """Crea el esquema y carga datos de ejemplo (idempotente)."""
        init_database(app)
        click.echo("Esquema y datos de ejemplo listos.")

    return app
