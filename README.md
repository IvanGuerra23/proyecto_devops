# CRUD Docker — API de Estudiantes

Proyecto académico de **DevOps** que evoluciona el CRUD original de Flask hacia una
aplicación contenerizada, con base de datos relacional, healthchecks, datos de
ejemplo, pruebas automatizadas y CI.

> **Estado: Avance 1.** El foco de este avance es la configuración del proyecto,
> la infraestructura DevOps y el modelo de datos (4 tablas). La API cubre
> consulta y creación de los recursos; actualización y borrado quedan para el
> siguiente avance.

## Arquitectura

```text
┌──────────────────┐        HTTP :5000        ┌──────────────────┐
│ Cliente (curl)   │ ───────────────────────► │ app (Flask)      │
│                  │                          │ Gunicorn + 2 w.  │
└──────────────────┘                          └────────┬─────────┘
                                                       │ SQL :3306
                                                       ▼
                                              ┌──────────────────┐
                                              │ db (MySQL 8.4)   │
                                              │ volumen: mysql_  │
                                              │ data             │
                                              └──────────────────┘
```

- `app` espera a que `db` esté **saludable** (`depends_on: service_healthy`).
- El entrypoint espera la conexión, crea el esquema y carga datos de ejemplo (idempotente).
- La aplicación corre con **usuario no root** y **Gunicorn**, no con el servidor de desarrollo.
- Adminer (opcional) permite inspeccionar la base desde el navegador.

## Modelo de datos

Cuatro tablas relacionadas:

```mermaid
erDiagram
    CARRERAS ||--o{ ESTUDIANTES : tiene
    ESTUDIANTES ||--o{ INSCRIPCIONES : realiza
    CURSOS ||--o{ INSCRIPCIONES : recibe
```

| Tabla          | Campos principales                                                                 |
| -------------- | ---------------------------------------------------------------------------------- |
| `carreras`     | `id`, `nombre` (único), `facultad`, `created_at`                                     |
| `estudiantes`  | `id`, `nombre`, `apellido`, `email` (único), `carrera_id` (FK), `fecha_registro`     |
| `cursos`       | `id`, `codigo` (único), `nombre`, `creditos`, `profesor`                             |
| `inscripciones`| `id`, `estudiante_id` (FK), `curso_id` (FK), `periodo`, `nota`, `fecha_registro`     |

`inscripciones` implementa la relación muchos-a-muchos entre estudiantes y cursos,
con restricción única por `(estudiante_id, curso_id, periodo)` y `nota` entre 0 y 20.

## Puesta en marcha

Requisitos: Docker Engine y Docker Compose v2.

```bash
# 1. (Opcional) personalizar credenciales y puertos
cp .env.example .env

# 2. Construir y levantar app + MySQL
make up

# 3. Verificar
curl http://localhost:5000/health
curl http://localhost:5000/estudiantes
```

Servicios:

| Servicio  | URL                          | Notas                                  |
| --------- | ---------------------------- | -------------------------------------- |
| API       | http://localhost:5000        | `APP_PORT` configurable                |
| MySQL     | `localhost:3307`             | `MYSQL_PORT`; usuario `devops`         |
| Adminer   | http://localhost:8081        | `make adminer` (perfil `tools`)        |

En Adminer usa: servidor `db`, usuario `devops`, contraseña `devops123` y base
`devops_db`.

Detener sin perder datos: `make down`. Borrar también la base: `make clean` (destructivo).

### Datos de ejemplo

Al iniciar con `SEED_DATA=true` se cargan 3 carreras, 4 cursos, 4 estudiantes y
5 inscripciones. La carga solo ocurre si la tabla `carreras` está vacía.

## Endpoints

| Método | Ruta                     | Descripción                                      |
| ------ | ------------------------ | ------------------------------------------------ |
| GET    | `/`                      | Información básica de la API                     |
| GET    | `/health`                | Estado de la app y de la conexión a la BD        |
| GET    | `/carreras`              | Lista de carreras                                |
| GET    | `/carreras/<id>`         | Detalle de una carrera                           |
| POST   | `/carreras`              | Crea una carrera (`nombre`, `facultad`)           |
| GET    | `/estudiantes`           | Lista estudiantes (`?carrera_id=` opcional)      |
| GET    | `/estudiantes/<id>`      | Detalle de un estudiante                         |
| POST   | `/estudiantes`           | Crea un estudiante                               |
| GET    | `/cursos`                | Lista de cursos                                  |
| GET    | `/cursos/<id>`           | Detalle de un curso                              |
| POST   | `/cursos`                | Crea un curso                                    |
| GET    | `/inscripciones`         | Lista inscripciones (`?estudiante_id=`, `?periodo=`) |
| GET    | `/inscripciones/<id>`    | Detalle de una inscripción                       |
| POST   | `/inscripciones`         | Inscribe a un estudiante en un curso             |

Ejemplos:

```bash
curl -X POST http://localhost:5000/carreras \
  -H 'Content-Type: application/json' \
  -d '{"nombre": "Ingeniería de Software", "facultad": "Ingeniería"}'

curl -X POST http://localhost:5000/estudiantes \
  -H 'Content-Type: application/json' \
  -d '{"nombre": "Ana", "apellido": "Pérez", "email": "ana@example.com", "carrera_id": 1}'

curl -X POST http://localhost:5000/inscripciones \
  -H 'Content-Type: application/json' \
  -d '{"estudiante_id": 1, "curso_id": 1, "periodo": "2026-II", "nota": 18.5}'
```

Errores uniformes: `400` validación, `404` recurso no encontrado, `409` duplicado,
`503` base de datos no disponible en `/health`.

## Variables de entorno

| Variable              | Defecto                       | Uso                                   |
| --------------------- | ----------------------------- | ------------------------------------- |
| `DATABASE_URL`        | SQLite en `instance/`         | Cadena de conexión (acepta `mysql://`)|
| `SECRET_KEY`          | valor de desarrollo           | Clave de Flask                        |
| `SEED_DATA`           | `true`                        | Cargar datos de ejemplo               |
| `MYSQL_DATABASE`      | `devops_db`                   | Base creada por MySQL                 |
| `MYSQL_USER`          | `devops`                      | Usuario de la aplicación              |
| `MYSQL_PASSWORD`      | `devops123`                   | Contraseña de la aplicación           |
| `MYSQL_ROOT_PASSWORD` | `rootpass`                    | Contraseña root (solo demo)           |
| `APP_PORT`            | `5000`                        | Puerto de la API en el host           |
| `MYSQL_PORT`          | `3307`                        | Puerto de MySQL en el host            |

> Para MySQL, `DATABASE_URL` debe usar el driver `mysql+pymysql://`.
> `config.py` normaliza el esquema corto `mysql://` automáticamente.

## Estructura

```text
crud-docker/
├── app/
│   ├── __init__.py          # Fábrica de la aplicación
│   ├── db_init.py           # Creación de esquema + seed
│   ├── extensions.py        # SQLAlchemy
│   ├── models.py            # 4 modelos relacionales
│   ├── seed.py              # Datos de ejemplo idempotentes
│   ├── utils.py             # Helpers de validación/errores
│   ├── wait_for_db.py       # Espera activa de la BD
│   └── routes/              # Blueprints: health, carreras, cursos, estudiantes, inscripciones
├── scripts/entrypoint.sh    # Entrypoint del contenedor
├── tests/                   # Pruebas con pytest
├── docs/avances.md          # Bitácora del proyecto
├── .github/workflows/ci.yml # CI: pruebas + build de imagen
├── config.py                # Configuración por entorno
├── app.py                   # Entrada para desarrollo local
├── wsgi.py                  # Entrada para Gunicorn
├── Dockerfile
├── docker-compose.yml
├── Makefile
└── requirements*.txt
```

## Desarrollo y pruebas

```bash
# Pruebas en contenedor (no requiere Python local)
make test

# Ejecución local con SQLite
python -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt
python app.py
```

La configuración de pruebas usa SQLite en memoria y no carga datos de ejemplo.

## CI

`.github/workflows/ci.yml` se ejecuta en cada push a `main` y en pull requests:

1. Instala dependencias y ejecuta `pytest`.
2. Construye la imagen Docker.

## Documentación del avance

La bitácora detallada (decisiones, evidencias y pendientes) está en
[`docs/avances.md`](docs/avances.md).

## Próximos pasos

- Completar CRUD (`PUT`/`PATCH` y `DELETE`) con pruebas.
- Migraciones de esquema con Flask-Migrate/Alembic.
- Publicación de imagen en un registry y despliegue.
- Observabilidad: logs estructurados y métricas.
