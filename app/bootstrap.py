"""Prepara la base de datos: migraciones + datos de ejemplo."""

from . import create_app
from .db_migrations import run_migrations
from .seed import load_seed_data


def main() -> int:
    app = create_app()
    run_migrations(app)

    with app.app_context():
        load_seed_data()

    print("[bootstrap] Base de datos preparada.", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
