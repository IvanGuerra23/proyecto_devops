"""Endpoints de carreras."""

from flask import Blueprint, jsonify
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from ..extensions import db
from ..models import Carrera
from ..utils import error, json_body, missing_fields

carreras_bp = Blueprint("carreras", __name__)


@carreras_bp.get("/carreras")
def listar_carreras():
    carreras = db.session.scalars(select(Carrera).order_by(Carrera.nombre)).all()
    return jsonify([carrera.to_dict() for carrera in carreras])


@carreras_bp.get("/carreras/<int:carrera_id>")
def obtener_carrera(carrera_id: int):
    carrera = db.session.get(Carrera, carrera_id)
    if carrera is None:
        return error("Carrera no encontrada", 404)
    return jsonify(carrera.to_dict())


@carreras_bp.post("/carreras")
def crear_carrera():
    data = json_body()
    if data is None:
        return error("El cuerpo de la petición debe ser JSON válido")

    faltantes = missing_fields(data, ("nombre", "facultad"))
    if faltantes:
        return error("Faltan campos obligatorios", campos=faltantes)

    nombre = str(data["nombre"]).strip()
    facultad = str(data["facultad"]).strip()
    if not nombre:
        return error("El nombre no puede estar vacío")
    if not facultad:
        return error("La facultad no puede estar vacía")

    carrera = Carrera(nombre=nombre, facultad=facultad)
    db.session.add(carrera)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return error("Ya existe una carrera con ese nombre", 409)

    return jsonify(carrera.to_dict()), 201


@carreras_bp.route("/carreras/<int:carrera_id>", methods=["PUT", "PATCH"])
def actualizar_carrera(carrera_id: int):
    carrera = db.session.get(Carrera, carrera_id)
    if carrera is None:
        return error("Carrera no encontrada", 404)

    data = json_body()
    if not data:
        return error("Envía al menos un campo para actualizar")

    campos_validos = {"nombre", "facultad"}
    if not campos_validos.intersection(data):
        return error("No se enviaron campos válidos", campos=sorted(campos_validos))

    if "nombre" in data:
        nombre = str(data["nombre"]).strip()
        if not nombre:
            return error("El nombre no puede estar vacío")
        carrera.nombre = nombre

    if "facultad" in data:
        facultad = str(data["facultad"]).strip()
        if not facultad:
            return error("La facultad no puede estar vacía")
        carrera.facultad = facultad

    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return error("Ya existe una carrera con ese nombre", 409)

    return jsonify(carrera.to_dict())


@carreras_bp.delete("/carreras/<int:carrera_id>")
def eliminar_carrera(carrera_id: int):
    carrera = db.session.get(Carrera, carrera_id)
    if carrera is None:
        return error("Carrera no encontrada", 404)

    if carrera.estudiantes:
        return error(
            "No se puede eliminar: la carrera tiene estudiantes asociados", 409
        )

    db.session.delete(carrera)
    db.session.commit()
    return "", 204
