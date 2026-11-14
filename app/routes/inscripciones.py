"""Endpoints de inscripciones (relación estudiantes - cursos)."""

from flask import Blueprint, jsonify, request
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from ..extensions import db
from ..models import Curso, Estudiante, Inscripcion
from ..utils import error, json_body, missing_fields

inscripciones_bp = Blueprint("inscripciones", __name__)


def _validar_nota(value):
    if value in (None, ""):
        return None, None

    try:
        nota = round(float(value), 2)
    except (TypeError, ValueError):
        return None, error("nota debe ser numérica")

    if not 0 <= nota <= 20:
        return None, error("nota debe estar entre 0 y 20")

    return nota, None


@inscripciones_bp.get("/inscripciones")
def listar_inscripciones():
    query = select(Inscripcion).order_by(Inscripcion.id)

    estudiante_id = request.args.get("estudiante_id", type=int)
    periodo = request.args.get("periodo")
    if estudiante_id is not None:
        query = query.where(Inscripcion.estudiante_id == estudiante_id)
    if periodo:
        query = query.where(Inscripcion.periodo == periodo)

    inscripciones = db.session.scalars(query).all()
    return jsonify([inscripcion.to_dict() for inscripcion in inscripciones])


@inscripciones_bp.get("/inscripciones/<int:inscripcion_id>")
def obtener_inscripcion(inscripcion_id: int):
    inscripcion = db.session.get(Inscripcion, inscripcion_id)
    if inscripcion is None:
        return error("Inscripción no encontrada", 404)
    return jsonify(inscripcion.to_dict())


@inscripciones_bp.post("/inscripciones")
def crear_inscripcion():
    data = json_body()
    if data is None:
        return error("El cuerpo de la petición debe ser JSON válido")

    faltantes = missing_fields(data, ("estudiante_id", "curso_id", "periodo"))
    if faltantes:
        return error("Faltan campos obligatorios", campos=faltantes)

    try:
        estudiante_id = int(data["estudiante_id"])
        curso_id = int(data["curso_id"])
    except (TypeError, ValueError):
        return error("estudiante_id y curso_id deben ser números enteros")

    if db.session.get(Estudiante, estudiante_id) is None:
        return error("El estudiante indicado no existe", 404)
    if db.session.get(Curso, curso_id) is None:
        return error("El curso indicado no existe", 404)

    nota, fallo = _validar_nota(data.get("nota"))
    if fallo:
        return fallo

    periodo = str(data["periodo"]).strip()
    if not periodo:
        return error("El periodo no puede estar vacío")

    repetida = db.session.scalar(
        select(Inscripcion).where(
            Inscripcion.estudiante_id == estudiante_id,
            Inscripcion.curso_id == curso_id,
            Inscripcion.periodo == periodo,
        )
    )
    if repetida is not None:
        return error(
            "El estudiante ya está inscrito en ese curso para el periodo", 409
        )

    inscripcion = Inscripcion(
        estudiante_id=estudiante_id,
        curso_id=curso_id,
        periodo=periodo,
        nota=nota,
    )
    db.session.add(inscripcion)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return error(
            "El estudiante ya está inscrito en ese curso para el periodo", 409
        )

    return jsonify(inscripcion.to_dict()), 201


@inscripciones_bp.route(
    "/inscripciones/<int:inscripcion_id>", methods=["PUT", "PATCH"]
)
def actualizar_inscripcion(inscripcion_id: int):
    inscripcion = db.session.get(Inscripcion, inscripcion_id)
    if inscripcion is None:
        return error("Inscripción no encontrada", 404)

    data = json_body()
    if not data:
        return error("Envía al menos un campo para actualizar")

    campos_validos = {"periodo", "nota"}
    if not campos_validos.intersection(data):
        return error("No se enviaron campos válidos", campos=sorted(campos_validos))

    periodo = inscripcion.periodo
    if "periodo" in data:
        periodo = str(data["periodo"]).strip()
        if not periodo:
            return error("El periodo no puede estar vacío")

    nota = inscripcion.nota
    if "nota" in data:
        nota, fallo = _validar_nota(data["nota"])
        if fallo:
            return fallo

    repetida = db.session.scalar(
        select(Inscripcion).where(
            Inscripcion.estudiante_id == inscripcion.estudiante_id,
            Inscripcion.curso_id == inscripcion.curso_id,
            Inscripcion.periodo == periodo,
            Inscripcion.id != inscripcion_id,
        )
    )
    if repetida is not None:
        return error(
            "El estudiante ya está inscrito en ese curso para el periodo", 409
        )

    inscripcion.periodo = periodo
    inscripcion.nota = nota

    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return error(
            "El estudiante ya está inscrito en ese curso para el periodo", 409
        )

    return jsonify(inscripcion.to_dict())


@inscripciones_bp.delete("/inscripciones/<int:inscripcion_id>")
def eliminar_inscripcion(inscripcion_id: int):
    inscripcion = db.session.get(Inscripcion, inscripcion_id)
    if inscripcion is None:
        return error("Inscripción no encontrada", 404)

    db.session.delete(inscripcion)
    db.session.commit()
    return "", 204
