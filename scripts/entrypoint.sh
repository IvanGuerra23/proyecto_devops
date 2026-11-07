#!/bin/sh
set -eu

echo "[entrypoint] Verificando conexión con la base de datos..."
python -m app.wait_for_db

echo "[entrypoint] Inicializando esquema y datos de ejemplo..."
flask --app app init-db

echo "[entrypoint] Iniciando servidor..."
exec "$@"
