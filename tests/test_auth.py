def test_pagina_login_publica(anon_client):
    respuesta = anon_client.get("/login")

    assert respuesta.status_code == 200
    assert b"Iniciar sesi" in respuesta.data
    assert b"app.js" not in respuesta.data


def test_api_requiere_autenticacion(anon_client):
    assert anon_client.get("/carreras").status_code == 401

    escritura = anon_client.post(
        "/carreras", json={"nombre": "X", "facultad": "Y"}
    )
    assert escritura.status_code == 401


def test_portada_redirige_al_login(anon_client):
    respuesta = anon_client.get("/")

    assert respuesta.status_code == 302
    assert "/login" in respuesta.headers["Location"]


def test_login_invalido(anon_client):
    respuesta = anon_client.post(
        "/login", json={"email": "admin@test.com", "password": "incorrecta"}
    )

    assert respuesta.status_code == 401
    assert respuesta.get_json()["error"] == "Credenciales inválidas"


def test_login_y_logout(anon_client):
    respuesta = anon_client.post(
        "/login", json={"email": "admin@test.com", "password": "admin123"}
    )

    assert respuesta.status_code == 200
    usuario = respuesta.get_json()["usuario"]
    assert usuario["rol"] == "admin"
    assert "password_hash" not in usuario

    assert anon_client.get("/carreras").status_code == 200

    salida = anon_client.post("/logout", json={})
    assert salida.status_code == 200
    assert anon_client.get("/carreras").status_code == 401


def test_lector_solo_lectura(viewer_client):
    assert viewer_client.get("/carreras").status_code == 200

    creacion = viewer_client.post(
        "/carreras", json={"nombre": "Nueva", "facultad": "Ingeniería"}
    )
    assert creacion.status_code == 403

    assert (
        viewer_client.patch("/carreras/1", json={"nombre": "Cambio"}).status_code
        == 403
    )
    assert viewer_client.delete("/carreras/1").status_code == 403


def test_admin_puede_escribir(client):
    respuesta = client.post(
        "/carreras", json={"nombre": "Ingeniería Civil", "facultad": "Ingeniería"}
    )

    assert respuesta.status_code == 201


def test_login_por_formulario_y_redireccion(anon_client):
    respuesta = anon_client.post(
        "/login",
        data={"email": "admin@test.com", "password": "admin123"},
        headers={"Accept": "text/html"},
    )

    assert respuesta.status_code == 302
    assert respuesta.headers["Location"].endswith("/")
