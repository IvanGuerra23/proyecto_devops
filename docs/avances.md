# Bitácora de avances

Registro cronológico de los avances del proyecto para la asignatura de DevOps.

---

## 2026-11-07 — Avance 1: configuración DevOps y modelo de datos

### Objetivo del avance

Pasar de un script Flask con Dockerfile básico a una base de proyecto ordenada:
configuración por entornos, orquestación con Docker Compose, base de datos MySQL
con al menos tres tablas relacionadas, verificación de salud, pruebas y CI.

### Actividades realizadas

- [x] **Reorganización del proyecto** con patrón *application factory*:
  `app/__init__.py`, `app/models.py`, `app/routes/`, `app/extensions.py`.
- [x] **Configuración centralizada** (`config.py`) por variables de entorno, con
  normalización automática de `mysql://` a `mysql+pymysql://` y configuración
  separada para pruebas.
- [x] **Modelo relacional de 4 tablas**: `carreras`, `estudiantes`, `cursos` e
  `inscripciones`, con claves foráneas, índices, restricciones de unicidad y
  borrado en cascada en las inscripciones.
- [x] **Datos de ejemplo idempotentes** (`app/seed.py`) que solo se cargan si la
  base está vacía: 3 carreras, 4 cursos, 4 estudiantes y 5 inscripciones.
- [x] **API organizada en blueprints** con validación de entrada y errores
  uniformes (`400`, `404`, `409`). Se añadieron consulta y creación de carreras,
  cursos e inscripciones; se conservó compatibilidad con `/estudiantes`.
- [x] **Endpoint `/health`** que comprueba la conexión real a la base de datos.
- [x] **Dockerfile de producción**: Python 3.12, usuario no root, Gunicorn,
  healthcheck y entrypoint con espera activa de la base.
- [x] **docker-compose.yml** con MySQL 8.4, volumen persistente, red dedicada,
  healthchecks, `depends_on` con `service_healthy` y Adminer opcional.
- [x] **Archivos de configuración**: `.env.example`, `.gitignore`, `.dockerignore`
  y `Makefile` con comandos frecuentes.
- [x] **Pruebas automatizadas** con pytest (SQLite en memoria) para salud,
  validaciones, duplicados y relaciones.
- [x] **Integración continua** en GitHub Actions: pruebas + build de la imagen.
- [x] **Documentación**: este documento y el `README.md` con arquitectura,
  endpoints, variables y comandos.

### Decisiones técnicas

| Decisión | Justificación |
| -------- | ------------- |
| MySQL 8.4 en Compose | Base relacional realista y reproducible; el volumen demuestra persistencia. |
| Gunicorn con 2 workers | Evita el servidor de desarrollo de Flask y se acerca a producción. |
| Entrypoint con espera + `depends_on: healthy` | Evita fallos de arranque cuando MySQL tarda en aceptar conexiones. |
| `create_all()` + seed idempotente | Suficiente para el avance; las migraciones (Alembic) quedan como siguiente paso. |
| SQLite en pruebas | Tests rápidos y sin dependencias externas. |
| Puerto 3307 para MySQL | Evita conflictos con un MySQL instalado en el host. |

### Evidencias para la demostración

```bash
# 1. Levantar el entorno
make up

# 2. Servicios y salud
make ps
curl http://localhost:5000/health
# {"status":"ok","database":"up"}

# 3. Datos de ejemplo
curl http://localhost:5000/carreras
curl http://localhost:5000/estudiantes
curl http://localhost:5000/inscripciones

# 4. Inspeccionar la base (opcional)
make adminer   # http://localhost:8081

# 5. Pruebas y CI
make test

# 6. Persistencia: reiniciar sin borrar datos
make down && make up
curl http://localhost:5000/estudiantes
```

### Pendientes para el siguiente avance

- Completar el CRUD con `PUT`/`PATCH` y `DELETE`.
- Introducir migraciones con Flask-Migrate.
- Publicar la imagen en un registry y documentar el despliegue.
- Añadir observabilidad (logs estructurados/métricas) y análisis de imagen.

---

## 2026-11-13 — Avance 2: CRUD completo e interfaz gráfica

### Objetivo del avance

Completar las operaciones de escritura de la API y ofrecer una interfaz gráfica
para administrar la información sin depender de `curl`, manteniendo el enfoque
DevOps y la calidad del avance anterior.

### Actividades realizadas

- [x] **CRUD completo en los cuatro recursos**: `PUT/PATCH` y `DELETE` para
  carreras, cursos, estudiantes e inscripciones.
- [x] **Actualizaciones parciales** con validación de campos, duplicados y
  referencias inexistentes (`400`, `404`, `409`).
- [x] **Borrado seguro**: se bloquea la eliminación de carreras con estudiantes,
  estudiantes con inscripciones y cursos con inscripciones. Las inscripciones se
  eliminan primero, dejando la integridad en manos de la aplicación.
- [x] **Interfaz gráfica** servida por Flask con Jinja2, CSS y JavaScript:
  panel con pestañas, contadores, tablas, formularios modales, edición, borrado,
  confirmaciones, notificaciones y estado de salud.
- [x] **Sin dependencias de frontend**: no hay CDN, bundler ni build step; la UI
  consume la API REST con `fetch`.
- [x] **Pruebas ampliadas a 11 casos**: CRUD, validaciones, relaciones
  protegidas, recursos inexistentes y carga del panel web.
- [x] **Documentación actualizada**: README con interfaz, endpoints completos y
  estructura; esta bitácora con evidencias.
- [x] **Validación end-to-end** contra MySQL en Docker Compose.

### Decisiones técnicas

| Decisión | Justificación |
| -------- | ------------- |
| UI en el mismo servicio Flask | Mantiene el avance simple y demuestra el consumo de la propia API sin añadir otro contenedor. |
| Jinja2 + JavaScript vanilla | Sin build step ni dependencias externas; fácil de reproducir y exponer. |
| `PUT` y `PATCH` con la misma semántica parcial | Simplifica la API y la UI; ambos actualizan solo los campos enviados. |
| Borrado bloqueado ante dependencias | Evita eliminaciones en cascada accidentales y hace explícito el orden de limpieza. |
| Edición de inscripciones limitada a periodo y nota | Cambiar estudiante/curso equivale a otra inscripción; evita estados inconsistentes. |
| Borrado de inscripciones como operación explícita | Permite liberar estudiantes y cursos antes de eliminarlos. |

### Evidencias para la demostración

```bash
# 1. Levantar el entorno
make up

# 2. Panel web
# http://localhost:5000/  -> crear, editar y eliminar registros

# 3. API completa
curl -X PATCH http://localhost:5000/estudiantes/1 \
  -H 'Content-Type: application/json' \
  -d '{"nombre": "Ana María"}'

curl -X PATCH http://localhost:5000/inscripciones/1 \
  -H 'Content-Type: application/json' \
  -d '{"nota": 19.5}'

# Borrado protegido (HTTP 409) y borrado permitido (HTTP 204)
curl -i -X DELETE http://localhost:5000/carreras/1

# 4. Pruebas
make test
# 11 passed

# 5. Estado
curl http://localhost:5000/health
```

### Pendientes para el siguiente avance

- Migraciones de esquema con Flask-Migrate/Alembic.
- Publicación de la imagen en un registry y despliegue documentado.
- Observabilidad: logs estructurados y métricas.
- Autenticación y roles para el panel.

---

## 2026-11-13 — Avance 3: migraciones, observabilidad y CI/CD de imagen

### Objetivo del avance

Dar madurez operativa al proyecto: versionar el esquema de la base de datos,
exponer señales de observabilidad y automatizar la publicación y el análisis de
la imagen, sin perder la compatibilidad con los datos de avances anteriores.

### Actividades realizadas

- [x] **Migraciones con Flask-Migrate/Alembic** (`migrations/`), con una
  migración inicial que reproduce las 4 tablas, índices, claves foráneas y
  restricciones únicas.
- [x] **Runner de migraciones** (`app/db_migrations.py`) que detecta bases
  heredadas sin `alembic_version`, aplica `stamp` en la revisión actual y luego
  ejecuta `upgrade`. Los datos existentes se conservan.
- [x] **Bootstrap de arranque** (`app/bootstrap.py`): espera la BD, aplica
  migraciones y carga el seed antes de iniciar Gunicorn.
- [x] **Logs estructurados JSON** con nivel configurable (`LOG_LEVEL`), duración,
  estado, ruta y `request_id`.
- [x] **Request IDs**: se acepta `X-Request-ID` del cliente o se genera uno; se
  devuelve siempre en la respuesta y se incluye en el log.
- [x] **Métricas Prometheus** en `/metrics`: `http_requests_total` y
  `http_request_duration_seconds` con etiquetas de método, endpoint y estado.
- [x] **Modo multiproceso** de `prometheus-client` para agregar métricas de los
  2 workers de Gunicorn (`PROMETHEUS_MULTIPROC_DIR`).
- [x] **Prometheus opcional** en Compose (perfil `observability`, puerto 9090)
  con `observability/prometheus.yml` apuntando a `app:5000/metrics`.
- [x] **CI/CD**: build de imagen, escaneo con Trivy y publicación en GHCR
  (`latest` y `sha-<commit>`) con `GITHUB_TOKEN` y `packages: write`.
- [x] **Imagen configurable** vía `APP_IMAGE`, para consumir la publicada en
  GHCR desde Compose.
- [x] **Pruebas ampliadas a 13 casos**, incluyendo `/metrics` y `X-Request-ID`.
- [x] **Validación end-to-end** de la migración sobre el volumen heredado y
  sobre una base vacía.

### Decisiones técnicas

| Decisión | Justificación |
| -------- | ------------- |
| Alembic como fuente del esquema | Permite evolucionar la base de forma reproducible y auditable. |
| `stamp` automático si faltan `alembic_version` | Evita recrear tablas en el volumen de avances previos conservando los datos. |
| Bootstrap antes de Gunicorn | Garantiza que la app nunca arranque con un esquema desactualizado. |
| Logs JSON con `X-Request-ID` | Facilita correlacionar peticiones y depurar en entornos contenerizados. |
| `prometheus-client` en modo multiproceso | Gunicorn usa 2 workers; sin esto las métricas se perderían entre procesos. |
| Prometheus en perfil opcional | Mantiene el arranque por defecto liviano y permite demostrar observabilidad cuando se necesita. |
| Trivy no bloqueante (`exit-code: 0`) | El objetivo del avance es informar vulnerabilidades sin frenar la entrega. |
| Tags `latest` + `sha-<commit>` en GHCR | `latest` para demo y el SHA para trazabilidad reproducible. |
| Renombrar `app/migrate.py` a `app/db_migrations.py` | Evita que el submódulo sobrescriba la extensión `migrate` del paquete `app`. |

### Evidencias para la demostración

```bash
# 1. Levantar el entorno (aplica migraciones automáticamente)
docker compose up -d --build

# 2. Verificar el estado y la versión del esquema
curl http://localhost:5000/health
docker compose exec -T db sh -c \
  'mysql -u$MYSQL_USER -p$MYSQL_PASSWORD $MYSQL_DATABASE -N \
   -e "SELECT version_num FROM alembic_version;"'
# d948fc81d8ad

# 3. Logs JSON y request ID
docker compose logs -f app
curl -H 'X-Request-ID: demo-abc-123' http://localhost:5000/health
# {"message": "http_request", ..., "request_id": "demo-abc-123"}

# 4. Métricas y Prometheus
curl http://localhost:5000/metrics | grep http_requests_total
docker compose --profile observability up -d prometheus
curl 'http://localhost:9090/api/v1/query?query=http_requests_total'

# 5. Pruebas
docker run --rm -e PYTHONDONTWRITEBYTECODE=1 -v "$PWD":/app -w /app \
  python:3.12-slim sh -c \
  "pip install -q -r requirements-dev.txt && python -m pytest -q -p no:cacheprovider"
# 13 passed

# 6. Migración en base vacía (camino alterno)
#    Se crea una base temporal y se ejecuta:
docker run --rm --network crud-docker_backend \
  -e DATABASE_URL='mysql+pymysql://devops:devops123@db:3306/devops_fresh?charset=utf8mb4' \
  --entrypoint python crud-docker-app:latest -m app.bootstrap
```

Resultados obtenidos en la validación:

| Verificación | Resultado |
| ------------ | --------- |
| Volumen heredado (sin `alembic_version`) | `stamp_revision -> d948fc81d8ad`, datos intactos (3 carreras, 4 cursos, 4 estudiantes, 5 inscripciones) |
| Base vacía | `upgrade -> d948fc81d8ad`, 4 tablas + `alembic_version`, seed cargado |
| `/metrics` | Métricas `http_requests_total` y `http_request_duration_seconds` presentes |
| Prometheus | Target `crud-docker-app` en estado `up` y consulta con 6 series |
| Logs | Línea JSON con `request_id: demo-abc-123` |
| Pruebas | **13 passed** |
| CI | Workflow con tests, build, Trivy y push a GHCR |

### Pendientes para el siguiente avance

- Autenticación y roles para el panel y la API.
- Despliegue documentado usando la imagen de GHCR.
- Alertas en Prometheus y dashboards en Grafana.
- Endurecimiento de la imagen y políticas de seguridad.

---

## 2026-11-14 — Avance 4: autenticación y roles

### Objetivo del avance

Cerrar el proyecto incorporando control de acceso al panel y a la API, con dos
roles claros (`admin` y `lector`), manteniendo la simplicidad y sin romper la
infraestructura, las migraciones, la observabilidad ni el CI/CD ya construidos.

### Actividades realizadas

- [x] **Autenticación por sesión con Flask-Login**: login/logout para el panel y
  la API, con la misma cookie de sesión firmada por Flask.
- [x] **Modelo `Usuario`** (`usuarios`) con `nombre`, `email` único,
  `password_hash`, `rol`, `activo` y `created_at`. Las contraseñas se almacenan
  con `generate_password_hash` de Werkzeug y nunca se devuelven por la API.
- [x] **Roles**: `admin` (CRUD completo) y `lector` (solo lectura).
- [x] **Protección centralizada** (`app/auth.py`): los blueprints académicos
  exigen sesión y las escrituras exigen rol `admin`; el rechazo es `401` sin
  sesión y `403` con rol insuficiente.
- [x] **Rutas públicas**: `/health` y `/metrics` siguen accesibles sin sesión
  para Docker, Prometheus y el CI.
- [x] **Panel web**: nueva página `/login`, datos del usuario y su rol en la
  barra superior, botón de salida y ocultamiento de las acciones de escritura
  para el rol `lector`. El JavaScript redirige a `/login` si la sesión expira.
- [x] **Cuentas demo idempotentes** creadas al arrancar (`SEED_USERS`,
  `SEED_ADMIN_*`, `SEED_VIEWER_*`): `admin@example.com / admin123` y
  `lector@example.com / lector123`.
- [x] **Migración `c73f1c202880`** que crea la tabla `usuarios`; se aplicó sobre
  el volumen existente sin recrear el esquema ni perder datos.
- [x] **Configuración de sesión**: `SESSION_COOKIE_HTTPONLY`, `SameSite=Lax` y
  `SESSION_COOKIE_SECURE` configurable para HTTPS.
- [x] **Redirección segura tras el login**: se valida `next` para evitar
  redirecciones abiertas.
- [x] **Pruebas ampliadas a 21 casos**: login correcto/incorrecto, logout,
  acceso anónimo (`401`), panel redirigido, `lector` en modo lectura (`403`) y
  `admin` con escritura.
- [x] **Validación end-to-end** contra MySQL en Docker Compose: login por API y
  formulario, roles, logout, métricas públicas y UI según rol.

### Decisiones técnicas

| Decisión | Justificación |
| -------- | ------------- |
| Sesiones con Flask-Login en vez de tokens | Menor complejidad para una app con panel web y API en el mismo servicio; el navegador ya maneja la cookie. |
| Dos roles fijos (`admin`, `lector`) | Cubre el requisito de roles sin introducir un sistema de permisos innecesario. |
| Protección a nivel de blueprint | Evita repetir decoradores en cada endpoint y garantiza que ninguna ruta nueva quede expuesta por olvido. |
| Escrituras solo para `admin` | El rol `lector` se define de forma consistente en API (`403`) y en la UI (botones ocultos). |
| `/health` y `/metrics` públicos | Docker, Prometheus y el CI no pueden autenticarse; exponerlos no compromete datos de negocio. |
| Cuentas demo sembradas desde variables de entorno | Permite probar la demo sin pasos manuales y cambiarlas en producción sin tocar código. |
| Sin CSRF token ni gestión de usuarios | Se prioriza mantener simple la última fase; el endurecimiento queda como trabajo futuro. |

### Evidencias para la demostración

```bash
# 1. Levantar el entorno (aplica la migración de usuarios)
docker compose up -d --build

# 2. Sin sesión: la API responde 401 y el panel redirige al login
curl -i http://localhost:5000/carreras          # 401
curl -i http://localhost:5000/                  # 302 -> /login

# 3. Login de administrador y CRUD
curl -c cookies.txt -X POST http://localhost:5000/login \
  -H 'Content-Type: application/json' \
  -d '{"email": "admin@example.com", "password": "admin123"}'
curl -b cookies.txt http://localhost:5000/carreras
curl -b cookies.txt -X POST http://localhost:5000/carreras \
  -H 'Content-Type: application/json' \
  -d '{"nombre": "Ingeniería Civil", "facultad": "Ingeniería"}'   # 201

# 4. Login de lector: solo lectura
curl -c lector.txt -X POST http://localhost:5000/login \
  -H 'Content-Type: application/json' \
  -d '{"email": "lector@example.com", "password": "lector123"}'
curl -b lector.txt http://localhost:5000/carreras                 # 200
curl -b lector.txt -X DELETE http://localhost:5000/carreras/1     # 403

# 5. Logout y métricas públicas
curl -b cookies.txt -c cookies.txt -X POST http://localhost:5000/logout
curl -b cookies.txt http://localhost:5000/carreras                # 401
curl http://localhost:5000/metrics                                # 200

# 6. Panel web
# http://localhost:5000/  -> admin ve crear/editar/eliminar
# http://localhost:5000/  -> lector solo consulta

# 7. Pruebas
docker run --rm -e PYTHONDONTWRITEBYTECODE=1 -v "$PWD":/app -w /app \
  python:3.12-slim sh -c \
  "pip install -q -r requirements-dev.txt && python -m pytest -q -p no:cacheprovider"
# 21 passed
```

Resultados obtenidos en la validación:

| Verificación | Resultado |
| ------------ | --------- |
| Migración sobre volumen existente | `upgrade d948fc81d8ad -> c73f1c202880`; datos intactos |
| Usuarios sembrados | `admin@example.com` (admin) y `lector@example.com` (lector), activos |
| API sin sesión | `401` en `/carreras`; `/` redirige a `/login` |
| Admin | `GET/POST/PATCH/DELETE` permitidos |
| Lector | `GET` permitido; escrituras `403` |
| Logout | La cookie deja de dar acceso (`401`) |
| Públicos | `/health` y `/metrics` siguen en `200` |
| Panel | Admin ve acciones; lector no las ve |
| Pruebas | **21 passed** |

### Pendientes / trabajo futuro

- Despliegue documentado usando la imagen publicada en GHCR.
- Gestión de usuarios desde el panel y cambio de contraseña.
- Protección CSRF para los formularios.
- Alertas en Prometheus y dashboards en Grafana (fuera del alcance acordado).
- Endurecimiento adicional de la imagen y políticas de seguridad.



