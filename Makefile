.DEFAULT_GOAL := help

.PHONY: help up down restart logs ps health adminer test shell db-shell clean

help: ## Muestra esta ayuda
	@grep -E '^[a-zA-Z_-]+:.*?## ' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-12s\033[0m %s\n", $$1, $$2}'

up: ## Construye y levanta app + MySQL en segundo plano
	docker compose up -d --build

down: ## Detiene los contenedores (conserva el volumen de MySQL)
	docker compose down

restart: ## Reinicia los servicios
	docker compose restart

logs: ## Sigue los logs de la app
	docker compose logs -f app

ps: ## Muestra el estado de los servicios
	docker compose ps

health: ## Consulta el endpoint de salud
	curl -fsS http://localhost:$${APP_PORT:-5000}/health

adminer: ## Levanta Adminer en http://localhost:8081
	docker compose --profile tools up -d adminer

test: ## Ejecuta las pruebas en un contenedor Python 3.12
	docker run --rm -e PYTHONDONTWRITEBYTECODE=1 -v "$$(pwd)":/app -w /app python:3.12-slim sh -c "pip install -q -r requirements-dev.txt && python -m pytest -q -p no:cacheprovider"

shell: ## Abre una shell dentro del contenedor de la app
	docker compose exec app sh

db-shell: ## Abre la consola de MySQL
	docker compose exec db sh -c 'mysql -u$$MYSQL_USER -p$$MYSQL_PASSWORD $$MYSQL_DATABASE'

clean: ## Elimina contenedores Y volumen de datos (¡borra la base!)
	docker compose down -v
