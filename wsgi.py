"""Punto de entrada para Gunicorn en el contenedor."""

from app import create_app

app = create_app()
