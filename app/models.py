"""Modelo relacional del dominio académico y de usuarios."""

from datetime import datetime, timezone

from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

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


class Usuario(UserMixin, db.Model):
    """Cuenta de acceso al panel y a la API."""

    __tablename__ = "usuarios"

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), nullable=False, unique=True)
    password_hash = db.Column(db.String(255), nullable=False)
    rol = db.Column(db.String(20), nullable=False, default="lector")
    activo = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(db.DateTime(timezone=True), default=utcnow, nullable=False)

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    @property
    def is_active(self) -> bool:
        return bool(self.activo)

    @property
    def is_admin(self) -> bool:
        return self.rol == "admin"

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "nombre": self.nombre,
            "email": self.email,
            "rol": self.rol,
            "activo": self.activo,
        }
