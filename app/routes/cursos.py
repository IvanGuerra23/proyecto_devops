"""Endpoints de cursos."""

from flask import Blueprint, jsonify
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from ..extensions import db
from ..models import Curso
from ..utils import error, json_body, missing_fields

cursos_bp = Blueprint("cursos", __name__)


@cursos_bp.get("/cursos")
def listar_cursos():
    cursos = db.session.scalars(select(Curso).order_by(Curso.nombre)).all()
    return jsonify([curso.to_dict() for curso in cursos])


@cursos_bp.get("/cursos/<int:curso_id>")
def obtener_curso(curso_id: int):
    curso = db.session.get(Curso, curso_id)
    if curso is None:
        return error("Curso no encontrado", 404)
    return jsonify(curso.to_dict())


@cursos_bp.post("/cursos")
def crear_curso():
    data = json_body()
    if data is None:
        return error("El cuerpo de la petición debe ser JSON válido")

    faltantes = missing_fields(data, ("codigo", "nombre", "creditos", "profesor"))
    if faltantes:
        return error("Faltan campos obligatorios", campos=faltantes)

    try:
        creditos = int(data["creditos"])
    except (TypeError, ValueError):
        return error("creditos debe ser un número entero")

    if creditos <= 0:
        return error("creditos debe ser mayor que cero")

    curso = Curso(
        codigo=str(data["codigo"]).strip().upper(),
        nombre=str(data["nombre"]).strip(),
        creditos=creditos,
        profesor=str(data["profesor"]).strip(),
    )
    db.session.add(curso)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return error("Ya existe un curso con ese código", 409)

    return jsonify(curso.to_dict()), 201
