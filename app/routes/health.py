"""Endpoint de salud usado por Docker, Compose y CI."""

from flask import Blueprint, current_app, jsonify
from sqlalchemy import text

from ..extensions import db

health_bp = Blueprint("health", __name__)


@health_bp.get("/health")
def health():
    try:
        db.session.execute(text("SELECT 1"))
        db.session.remove()
    except Exception:
        current_app.logger.exception("El healthcheck de la base de datos falló")
        return jsonify({"status": "error", "database": "down"}), 503

    return jsonify({"status": "ok", "database": "up"}), 200
