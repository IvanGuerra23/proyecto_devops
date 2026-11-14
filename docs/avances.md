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

