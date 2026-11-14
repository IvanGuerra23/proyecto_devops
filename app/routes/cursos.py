"""Endpoints de cursos."""

from flask import Blueprint, jsonify
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from ..extensions import db
from ..models import Curso
from ..utils import error, json_body, missing_fields

cursos_bp = Blueprint("cursos", __name__)


def _validar_creditos(value):
    try:
        creditos = int(value)
    except (TypeError, ValueError):
        return None, error("creditos debe ser un número entero")

    if creditos <= 0:
        return None, error("creditos debe ser mayor que cero")

    return creditos, None


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

    creditos, fallo = _validar_creditos(data["creditos"])
    if fallo:
        return fallo

    codigo = str(data["codigo"]).strip().upper()
    nombre = str(data["nombre"]).strip()
    profesor = str(data["profesor"]).strip()
    if not codigo:
        return error("El código no puede estar vacío")
    if not nombre:
        return error("El nombre no puede estar vacío")
    if not profesor:
        return error("El profesor no puede estar vacío")

    curso = Curso(
        codigo=codigo,
        nombre=nombre,
        creditos=creditos,
        profesor=profesor,
    )
    db.session.add(curso)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return error("Ya existe un curso con ese código", 409)

    return jsonify(curso.to_dict()), 201


@cursos_bp.route("/cursos/<int:curso_id>", methods=["PUT", "PATCH"])
def actualizar_curso(curso_id: int):
    curso = db.session.get(Curso, curso_id)
    if curso is None:
        return error("Curso no encontrado", 404)

    data = json_body()
    if not data:
        return error("Envía al menos un campo para actualizar")

    campos_validos = {"codigo", "nombre", "creditos", "profesor"}
    if not campos_validos.intersection(data):
        return error("No se enviaron campos válidos", campos=sorted(campos_validos))

    if "codigo" in data:
        codigo = str(data["codigo"]).strip().upper()
        if not codigo:
            return error("El código no puede estar vacío")
        curso.codigo = codigo

    if "nombre" in data:
        nombre = str(data["nombre"]).strip()
        if not nombre:
            return error("El nombre no puede estar vacío")
        curso.nombre = nombre

    if "creditos" in data:
        creditos, fallo = _validar_creditos(data["creditos"])
        if fallo:
            return fallo
        curso.creditos = creditos

    if "profesor" in data:
        profesor = str(data["profesor"]).strip()
        if not profesor:
            return error("El profesor no puede estar vacío")
        curso.profesor = profesor

    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return error("Ya existe un curso con ese código", 409)

    return jsonify(curso.to_dict())


@cursos_bp.delete("/cursos/<int:curso_id>")
def eliminar_curso(curso_id: int):
    curso = db.session.get(Curso, curso_id)
    if curso is None:
        return error("Curso no encontrado", 404)

    if curso.inscripciones:
        return error(
            "No se puede eliminar: el curso tiene inscripciones asociadas", 409
        )

    db.session.delete(curso)
    db.session.commit()
    return "", 204
