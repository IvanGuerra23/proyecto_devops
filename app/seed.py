"""Datos de ejemplo para la demostración del avance."""

from flask import current_app
from sqlalchemy import select

from .extensions import db
from .models import Carrera, Curso, Estudiante, Inscripcion, Usuario


def load_seed_data() -> None:
    """Carga datos solo si la tabla de carreras está vacía (idempotente)."""
    if db.session.scalar(select(Carrera.id).limit(1)) is not None:
        return

    carreras = {
        "sistemas": Carrera(
            nombre="Ingeniería de Sistemas", facultad="Ingeniería"
        ),
        "industrial": Carrera(
            nombre="Ingeniería Industrial", facultad="Ingeniería"
        ),
        "administracion": Carrera(
            nombre="Administración de Empresas", facultad="Ciencias Económicas"
        ),
    }

    cursos = {
        "devops": Curso(
            codigo="DEVOPS-01",
            nombre="Fundamentos de DevOps",
            creditos=4,
            profesor="Iván Guerra",
        ),
        "bd": Curso(
            codigo="BD-02",
            nombre="Bases de Datos",
            creditos=4,
            profesor="Laura Méndez",
        ),
        "web": Curso(
            codigo="WEB-03",
            nombre="Programación Web",
            creditos=3,
            profesor="Carlos Rojas",
        ),
        "redes": Curso(
            codigo="REDES-04",
            nombre="Redes de Computadores",
            creditos=3,
            profesor="Sofía Torres",
        ),
    }

    db.session.add_all([*carreras.values(), *cursos.values()])
    db.session.flush()

    estudiantes = [
        Estudiante(
            nombre="Ana",
            apellido="Pérez",
            email="ana.perez@example.com",
            carrera=carreras["sistemas"],
        ),
        Estudiante(
            nombre="Luis",
            apellido="Gómez",
            email="luis.gomez@example.com",
            carrera=carreras["sistemas"],
        ),
        Estudiante(
            nombre="María",
            apellido="Rodríguez",
            email="maria.rodriguez@example.com",
            carrera=carreras["industrial"],
        ),
        Estudiante(
            nombre="Jorge",
            apellido="Ramírez",
            email="jorge.ramirez@example.com",
            carrera=carreras["administracion"],
        ),
    ]
    db.session.add_all(estudiantes)
    db.session.flush()

    db.session.add_all(
        [
            Inscripcion(
                estudiante=estudiantes[0],
                curso=cursos["devops"],
                periodo="2026-II",
                nota=18.5,
            ),
            Inscripcion(
                estudiante=estudiantes[0],
                curso=cursos["bd"],
                periodo="2026-II",
                nota=17.0,
            ),
            Inscripcion(
                estudiante=estudiantes[1],
                curso=cursos["devops"],
                periodo="2026-II",
                nota=15.5,
            ),
            Inscripcion(
                estudiante=estudiantes[2],
                curso=cursos["web"],
                periodo="2026-II",
                nota=None,
            ),
            Inscripcion(
                estudiante=estudiantes[3],
                curso=cursos["redes"],
                periodo="2026-II",
                nota=19.0,
            ),
        ]
    )
    db.session.commit()


def ensure_default_users() -> None:
    """Crea las cuentas demo solo si su email no existe (idempotente)."""
    if not current_app.config.get("SEED_USERS", True):
        return

    cuentas = (
        (
            current_app.config["SEED_ADMIN_EMAIL"],
            current_app.config["SEED_ADMIN_PASSWORD"],
            "Administrador",
            "admin",
        ),
        (
            current_app.config["SEED_VIEWER_EMAIL"],
            current_app.config["SEED_VIEWER_PASSWORD"],
            "Consulta",
            "lector",
        ),
    )

    creados = 0
    for email, password, nombre, rol in cuentas:
        email = str(email or "").strip().lower()
        if not email or not password:
            continue
        existente = db.session.scalar(
            select(Usuario).where(Usuario.email == email)
        )
        if existente is not None:
            continue

        usuario = Usuario(nombre=nombre, email=email, rol=rol)
        usuario.set_password(password)
        db.session.add(usuario)
        creados += 1

    if creados:
        db.session.commit()

