import pytest

from app import create_app
from app.extensions import db
from app.models import Usuario


def _crear_usuarios():
    admin = Usuario(nombre="Admin", email="admin@test.com", rol="admin")
    admin.set_password("admin123")

    lector = Usuario(nombre="Lector", email="lector@test.com", rol="lector")
    lector.set_password("lector123")

    db.session.add_all([admin, lector])
    db.session.commit()


@pytest.fixture()
def app():
    application = create_app("config.TestingConfig")

    with application.app_context():
        db.create_all()
        _crear_usuarios()
        yield application
        db.session.remove()
        db.drop_all()


@pytest.fixture()
def anon_client(app):
    return app.test_client()


@pytest.fixture()
def client(app):
    cliente = app.test_client()
    respuesta = cliente.post(
        "/login", json={"email": "admin@test.com", "password": "admin123"}
    )
    assert respuesta.status_code == 200
    return cliente


@pytest.fixture()
def viewer_client(app):
    cliente = app.test_client()
    respuesta = cliente.post(
        "/login", json={"email": "lector@test.com", "password": "lector123"}
    )
    assert respuesta.status_code == 200
    return cliente
