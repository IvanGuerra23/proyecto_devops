"""Espera de forma activa a que la base de datos esté disponible.

Se ejecuta desde el entrypoint del contenedor antes de inicializar el
esquema y arrancar Gunicorn.
"""

import sys
import time

from sqlalchemy import text

from . import create_app
from .extensions import db

MAX_INTENTOS = 30
ESPERA_SEGUNDOS = 2


def main() -> int:
    app = create_app()

    with app.app_context():
        for intento in range(1, MAX_INTENTOS + 1):
            try:
                db.session.execute(text("SELECT 1"))
                db.session.remove()
                print(
                    f"[wait-for-db] Base de datos disponible (intento {intento}).",
                    flush=True,
                )
                return 0
            except Exception:
                db.session.remove()
                print(
                    f"[wait-for-db] Esperando base de datos... "
                    f"({intento}/{MAX_INTENTOS})",
                    flush=True,
                )
                time.sleep(ESPERA_SEGUNDOS)

    print(
        "[wait-for-db] No fue posible conectar con la base de datos.",
        file=sys.stderr,
    )
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
