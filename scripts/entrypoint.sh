#!/bin/sh
set -eu

echo "[entrypoint] Verificando conexión con la base de datos..."
python -m app.wait_for_db

echo "[entrypoint] Aplicando migraciones y datos de ejemplo..."
python -m app.bootstrap

if [ -n "${PROMETHEUS_MULTIPROC_DIR:-}" ]; then
  rm -rf "${PROMETHEUS_MULTIPROC_DIR:?}"/* 2>/dev/null || true
  mkdir -p "$PROMETHEUS_MULTIPROC_DIR"
fi

echo "[entrypoint] Iniciando servidor..."
exec "$@"
