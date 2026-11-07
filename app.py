"""Punto de entrada para desarrollo local (sin Gunicorn)."""

from app import create_app
from app.db_init import init_database

app = create_app()


if __name__ == "__main__":
    init_database(app)
    app.run(host="0.0.0.0", port=5000)
