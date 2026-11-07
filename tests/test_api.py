def crear_carrera(client, nombre="Ingeniería de Sistemas"):
    respuesta = client.post(
        "/carreras", json={"nombre": nombre, "facultad": "Ingeniería"}
    )
    assert respuesta.status_code == 201
    return respuesta.get_json()["id"]


def crear_estudiante(client, carrera_id, email="ana.perez@example.com"):
    return client.post(
        "/estudiantes",
        json={
            "nombre": "Ana",
            "apellido": "Pérez",
            "email": email,
            "carrera_id": carrera_id,
        },
    )


def test_health(client):
    respuesta = client.get("/health")

    assert respuesta.status_code == 200
    assert respuesta.get_json() == {"status": "ok", "database": "up"}


def test_crear_y_listar_estudiante(client):
    carrera_id = crear_carrera(client)

    respuesta = crear_estudiante(client, carrera_id)

    assert respuesta.status_code == 201
    assert respuesta.get_json()["carrera"] == "Ingeniería de Sistemas"

    listado = client.get("/estudiantes")
    assert listado.status_code == 200
    assert len(listado.get_json()) == 1


def test_validaciones_de_estudiante(client):
    incompleto = client.post("/estudiantes", json={"nombre": "Ana"})

    assert incompleto.status_code == 400
    assert "email" in incompleto.get_json()["campos"]

    carrera_id = crear_carrera(client)
    assert crear_estudiante(client, carrera_id).status_code == 201

    duplicado = crear_estudiante(client, carrera_id)
    assert duplicado.status_code == 409


def test_inscripcion_valida_relaciones(client):
    carrera_id = crear_carrera(client)
    estudiante = crear_estudiante(client, carrera_id).get_json()

    curso = client.post(
        "/cursos",
        json={
            "codigo": "DEVOPS-01",
            "nombre": "Fundamentos de DevOps",
            "creditos": 4,
            "profesor": "Iván Guerra",
        },
    ).get_json()

    respuesta = client.post(
        "/inscripciones",
        json={
            "estudiante_id": estudiante["id"],
            "curso_id": curso["id"],
            "periodo": "2026-II",
            "nota": 18.5,
        },
    )

    assert respuesta.status_code == 201
    assert respuesta.get_json()["nota"] == 18.5

    repetida = client.post(
        "/inscripciones",
        json={
            "estudiante_id": estudiante["id"],
            "curso_id": curso["id"],
            "periodo": "2026-II",
        },
    )
    assert repetida.status_code == 409
