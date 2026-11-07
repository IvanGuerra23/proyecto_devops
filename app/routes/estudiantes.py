"""Endpoints de estudiantes."""

from flask import Blueprint, jsonify, request
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from ..extensions import db
from ..models import Carrera, Estudiante
from ..utils import error, json_body, missing_fields

estudiantes_bp = Blueprint("estudiantes", __name__)


@estudiantes_bp.get("/estudiantes")
def listar_estudiantes():
    query = select(Estudiante).order_by(Estudiante.id)

    carrera_id = request.args.get("carrera_id", type=int)
    if carrera_id is not None:
        query = query.where(Estudiante.carrera_id == carrera_id)

    estudiantes = db.session.scalars(query).all()
    return jsonify([estudiante.to_dict() for estudiante in estudiantes])


@estudiantes_bp.get("/estudiantes/<int:estudiante_id>")
def obtener_estudiante(estudiante_id: int):
    estudiante = db.session.get(Estudiante, estudiante_id)
    if estudiante is None:
        return error("Estudiante no encontrado", 404)
    return jsonify(estudiante.to_dict())


@estudiantes_bp.post("/estudiantes")
def crear_estudiante():
    data = json_body()
    if data is None:
        return error("El cuerpo de la petición debe ser JSON válido")

    faltantes = missing_fields(
        data, ("nombre", "apellido", "email", "carrera_id")
    )
    if faltantes:
        return error("Faltan campos obligatorios", campos=faltantes)

    try:
        carrera_id = int(data["carrera_id"])
    except (TypeError, ValueError):
        return error("carrera_id debe ser un número entero")

    if db.session.get(Carrera, carrera_id) is None:
        return error("La carrera indicada no existe", 404)

    email = str(data["email"]).strip().lower()
    existente = db.session.scalar(
        select(Estudiante).where(Estudiante.email == email)
    )
    if existente is not None:
        return error("El email ya está registrado", 409)

    estudiante = Estudiante(
        nombre=str(data["nombre"]).strip(),
        apellido=str(data["apellido"]).strip(),
        email=email,
        carrera_id=carrera_id,
    )
    db.session.add(estudiante)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return error("El email ya está registrado", 409)

    return jsonify(estudiante.to_dict()), 201
