"""Punto de entrada para desarrollo local (sin Gunicorn)."""

from app import create_app
from app.db_migrations import run_migrations
from app.seed import load_seed_data

app = create_app()


if __name__ == "__main__":
    run_migrations(app)
    with app.app_context():
        load_seed_data()
    app.run(host="0.0.0.0", port=5000)
