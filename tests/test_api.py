def crear_carrera(client, nombre="Ingeniería de Sistemas"):
    respuesta = client.post(
        "/carreras", json={"nombre": nombre, "facultad": "Ingeniería"}
    )
    assert respuesta.status_code == 201
    return respuesta.get_json()["id"]


def crear_estudiante(client, carrera_id, email="ana.perez@example.com"):
    respuesta = client.post(
        "/estudiantes",
        json={
            "nombre": "Ana",
            "apellido": "Pérez",
            "email": email,
            "carrera_id": carrera_id,
        },
    )
    assert respuesta.status_code == 201
    return respuesta.get_json()


def crear_curso(client, codigo="DEVOPS-01"):
    respuesta = client.post(
        "/cursos",
        json={
            "codigo": codigo,
            "nombre": "Fundamentos de DevOps",
            "creditos": 4,
            "profesor": "Iván Guerra",
        },
    )
    assert respuesta.status_code == 201
    return respuesta.get_json()


def crear_inscripcion(client, estudiante_id, curso_id, nota=18.5):
    return client.post(
        "/inscripciones",
        json={
            "estudiante_id": estudiante_id,
            "curso_id": curso_id,
            "periodo": "2026-II",
            "nota": nota,
        },
    )


def test_health(anon_client):
    respuesta = anon_client.get("/health")

    assert respuesta.status_code == 200
    assert respuesta.get_json() == {"status": "ok", "database": "up"}


def test_interfaz_grafica(client):
    respuesta = client.get("/")

    assert respuesta.status_code == 200
    assert b"Panel de control" in respuesta.data
    assert b"app.js" in respuesta.data


def test_metrics_expone_prometheus(anon_client):
    anon_client.get("/health")

    respuesta = anon_client.get("/metrics")

    assert respuesta.status_code == 200
    assert respuesta.content_type.startswith("text/plain")
    cuerpo = respuesta.data.decode()
    assert "http_requests_total" in cuerpo
    assert "http_request_duration_seconds" in cuerpo


def test_request_id_propio_y_generado(client):
    propio = client.get("/health", headers={"X-Request-ID": "demo-123"})
    assert propio.headers["X-Request-ID"] == "demo-123"

    generado = client.get("/health")
    assert len(generado.headers["X-Request-ID"]) == 12


def test_crear_y_listar_estudiante(client):
    carrera_id = crear_carrera(client)
    estudiante = crear_estudiante(client, carrera_id)

    assert estudiante["carrera"] == "Ingeniería de Sistemas"

    listado = client.get("/estudiantes")
    assert listado.status_code == 200
    assert len(listado.get_json()) == 1


def test_validaciones_de_estudiante(client):
    incompleto = client.post("/estudiantes", json={"nombre": "Ana"})

    assert incompleto.status_code == 400
    assert "email" in incompleto.get_json()["campos"]

    carrera_id = crear_carrera(client)
    assert crear_estudiante(client, carrera_id)["id"] == 1

    duplicado = client.post(
        "/estudiantes",
        json={
            "nombre": "Otra",
            "apellido": "Persona",
            "email": "ana.perez@example.com",
            "carrera_id": carrera_id,
        },
    )
    assert duplicado.status_code == 409


def test_actualizar_estudiante(client):
    carrera_id = crear_carrera(client)
    estudiante = crear_estudiante(client, carrera_id)

    respuesta = client.patch(
        f"/estudiantes/{estudiante['id']}",
        json={"nombre": "Ana María", "email": "ana.maria@example.com"},
    )

    assert respuesta.status_code == 200
    actualizado = respuesta.get_json()
    assert actualizado["nombre"] == "Ana María"
    assert actualizado["email"] == "ana.maria@example.com"

    detalle = client.get(f"/estudiantes/{estudiante['id']}")
    assert detalle.get_json()["nombre"] == "Ana María"


def test_inscripcion_valida_relaciones(client):
    carrera_id = crear_carrera(client)
    estudiante = crear_estudiante(client, carrera_id)
    curso = crear_curso(client)

    respuesta = crear_inscripcion(client, estudiante["id"], curso["id"])

    assert respuesta.status_code == 201
    assert respuesta.get_json()["nota"] == 18.5

    repetida = crear_inscripcion(client, estudiante["id"], curso["id"])
    assert repetida.status_code == 409


def test_actualizar_inscripcion_y_limpiar_nota(client):
    carrera_id = crear_carrera(client)
    estudiante = crear_estudiante(client, carrera_id)
    curso = crear_curso(client)
    inscripcion = crear_inscripcion(
        client, estudiante["id"], curso["id"]
    ).get_json()

    respuesta = client.patch(
        f"/inscripciones/{inscripcion['id']}",
        json={"nota": 19.5, "periodo": "2027-I"},
    )

    assert respuesta.status_code == 200
    actualizada = respuesta.get_json()
    assert actualizada["nota"] == 19.5
    assert actualizada["periodo"] == "2027-I"

    sin_nota = client.patch(
        f"/inscripciones/{inscripcion['id']}", json={"nota": None}
    )
    assert sin_nota.status_code == 200
    assert sin_nota.get_json()["nota"] is None


def test_eliminar_estudiante_protegido_por_inscripcion(client):
    carrera_id = crear_carrera(client)
    estudiante = crear_estudiante(client, carrera_id)
    curso = crear_curso(client)
    inscripcion = crear_inscripcion(
        client, estudiante["id"], curso["id"]
    ).get_json()

    protegido = client.delete(f"/estudiantes/{estudiante['id']}")
    assert protegido.status_code == 409

    assert client.delete(f"/inscripciones/{inscripcion['id']}").status_code == 204
    assert client.delete(f"/estudiantes/{estudiante['id']}").status_code == 204
    assert client.get(f"/estudiantes/{estudiante['id']}").status_code == 404


def test_eliminar_carrera_protegida_por_estudiantes(client):
    carrera_id = crear_carrera(client)
    estudiante = crear_estudiante(client, carrera_id)

    assert client.delete(f"/carreras/{carrera_id}").status_code == 409
    assert client.delete(f"/estudiantes/{estudiante['id']}").status_code == 204
    assert client.delete(f"/carreras/{carrera_id}").status_code == 204


def test_eliminar_curso_protegido_por_inscripciones(client):
    carrera_id = crear_carrera(client)
    estudiante = crear_estudiante(client, carrera_id)
    curso = crear_curso(client)
    inscripcion = crear_inscripcion(
        client, estudiante["id"], curso["id"]
    ).get_json()

    assert client.delete(f"/cursos/{curso['id']}").status_code == 409
    assert client.delete(f"/inscripciones/{inscripcion['id']}").status_code == 204
    assert client.delete(f"/cursos/{curso['id']}").status_code == 204


def test_recursos_inexistentes(client):
    assert client.get("/estudiantes/999").status_code == 404
    assert (
        client.patch("/estudiantes/999", json={"nombre": "X"}).status_code == 404
    )
    assert client.delete("/carreras/999").status_code == 404
    assert client.get("/inscripciones/999").status_code == 404
