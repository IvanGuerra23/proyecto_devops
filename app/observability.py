"""Observabilidad: logs JSON, request IDs y métricas Prometheus."""

import json
import logging
import os
import time
import uuid

from flask import Flask, Response, g, request
from prometheus_client import (
    CONTENT_TYPE_LATEST,
    CollectorRegistry,
    Counter,
    Histogram,
    generate_latest,
    multiprocess,
)

REQUEST_COUNT = Counter(
    "http_requests_total",
    "Número total de peticiones HTTP",
    ["method", "endpoint", "status"],
)
REQUEST_LATENCY = Histogram(
    "http_request_duration_seconds",
    "Duración de las peticiones HTTP en segundos",
    ["method", "endpoint"],
)


class JsonFormatter(logging.Formatter):
    """Formatea cada registro de log como una línea JSON."""

    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "timestamp": self.formatTime(record, "%Y-%m-%dT%H:%M:%S%z"),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        payload.update(getattr(record, "extra_data", {}))
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        return json.dumps(payload, ensure_ascii=False)


def _configurar_logging(app: Flask) -> None:
    handler = logging.StreamHandler()
    handler.setFormatter(JsonFormatter())
    app.logger.handlers = [handler]
    app.logger.propagate = False
    app.logger.setLevel(app.config.get("LOG_LEVEL", "INFO"))


def _registrar_metricas(app: Flask) -> None:
    @app.before_request
    def _iniciar_peticion() -> None:
        g.request_id = request.headers.get("X-Request-ID") or uuid.uuid4().hex[:12]
        g.request_start = time.perf_counter()

    @app.after_request
    def _finalizar_peticion(response: Response) -> Response:
        duracion = time.perf_counter() - getattr(
            g, "request_start", time.perf_counter()
        )
        endpoint = request.endpoint or "unmatched"

        REQUEST_COUNT.labels(
            request.method, endpoint, str(response.status_code)
        ).inc()
        REQUEST_LATENCY.labels(request.method, endpoint).observe(duracion)

        request_id = getattr(g, "request_id", "-")
        response.headers["X-Request-ID"] = request_id
        app.logger.info(
            "http_request",
            extra={
                "extra_data": {
                    "method": request.method,
                    "path": request.path,
                    "status": response.status_code,
                    "duration_ms": round(duracion * 1000, 2),
                    "request_id": request_id,
                    "remote_addr": request.headers.get(
                        "X-Forwarded-For", request.remote_addr
                    ),
                }
            },
        )
        return response

    @app.get("/metrics")
    def metrics():
        """Expone las métricas en formato Prometheus."""
        if os.getenv("PROMETHEUS_MULTIPROC_DIR"):
            registry = CollectorRegistry()
            multiprocess.MultiProcessCollector(registry)
            payload = generate_latest(registry)
        else:
            payload = generate_latest()

        return Response(
            payload,
            headers={"Content-Type": CONTENT_TYPE_LATEST},
        )


def init_observability(app: Flask) -> None:
    """Configura logs estructurados, request IDs y métricas."""
    _configurar_logging(app)
    _registrar_metricas(app)
