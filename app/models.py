"""Modelo relacional del dominio académico (4 tablas)."""

from datetime import datetime, timezone

from .extensions import db


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Carrera(db.Model):
    __tablename__ = "carreras"

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(80), nullable=False, unique=True)
    facultad = db.Column(db.String(80), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), default=utcnow, nullable=False)

    estudiantes = db.relationship(
        "Estudiante", back_populates="carrera", cascade="all, delete-orphan"
    )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "nombre": self.nombre,
            "facultad": self.facultad,
            "total_estudiantes": len(self.estudiantes),
        }


class Estudiante(db.Model):
    __tablename__ = "estudiantes"

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(80), nullable=False)
    apellido = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), nullable=False, unique=True)
    carrera_id = db.Column(
        db.Integer,
        db.ForeignKey("carreras.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    fecha_registro = db.Column(
        db.DateTime(timezone=True), default=utcnow, nullable=False
    )

    carrera = db.relationship("Carrera", back_populates="estudiantes")
    inscripciones = db.relationship(
        "Inscripcion", back_populates="estudiante", cascade="all, delete-orphan"
    )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "nombre": self.nombre,
            "apellido": self.apellido,
            "email": self.email,
            "carrera_id": self.carrera_id,
            "carrera": self.carrera.nombre if self.carrera else None,
            "fecha_registro": self.fecha_registro.isoformat(),
        }


class Curso(db.Model):
    __tablename__ = "cursos"

    id = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(20), nullable=False, unique=True)
    nombre = db.Column(db.String(100), nullable=False)
    creditos = db.Column(db.Integer, nullable=False)
    profesor = db.Column(db.String(100), nullable=False)

    inscripciones = db.relationship(
        "Inscripcion", back_populates="curso", cascade="all, delete-orphan"
    )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "codigo": self.codigo,
            "nombre": self.nombre,
            "creditos": self.creditos,
            "profesor": self.profesor,
        }


class Inscripcion(db.Model):
    __tablename__ = "inscripciones"
    __table_args__ = (
        db.UniqueConstraint(
            "estudiante_id",
            "curso_id",
            "periodo",
            name="uq_inscripcion_estudiante_curso_periodo",
        ),
    )

    id = db.Column(db.Integer, primary_key=True)
    estudiante_id = db.Column(
        db.Integer,
        db.ForeignKey("estudiantes.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    curso_id = db.Column(
        db.Integer,
        db.ForeignKey("cursos.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    periodo = db.Column(db.String(20), nullable=False)
    nota = db.Column(db.Numeric(4, 2), nullable=True)
    fecha_registro = db.Column(
        db.DateTime(timezone=True), default=utcnow, nullable=False
    )

    estudiante = db.relationship("Estudiante", back_populates="inscripciones")
    curso = db.relationship("Curso", back_populates="inscripciones")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "estudiante_id": self.estudiante_id,
            "curso_id": self.curso_id,
            "periodo": self.periodo,
            "nota": float(self.nota) if self.nota is not None else None,
            "fecha_registro": self.fecha_registro.isoformat(),
        }
