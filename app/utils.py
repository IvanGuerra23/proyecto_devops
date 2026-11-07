"""Utilidades compartidas por los endpoints."""

from flask import jsonify, request


def json_body():
    """Devuelve el cuerpo JSON o ``None`` si no es un JSON válido."""
    return request.get_json(silent=True)


def missing_fields(data: dict, fields: tuple[str, ...]) -> list[str]:
    """Lista los campos obligatorios ausentes o vacíos."""
    return [field for field in fields if data.get(field) in (None, "")]


def error(message: str, status: int = 400, **extra):
    """Construye una respuesta de error uniforme."""
    payload = {"error": message}
    payload.update(extra)
    return jsonify(payload), status
