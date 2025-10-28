# File: app/metrics_setup.py

import time

from prometheus_client import REGISTRY, Counter, Gauge, Histogram, generate_latest
from starlette.requests import Request
from starlette.responses import Response

# --- 1. SRE METRICS DEFINITION ---
# (Definitions remain the same)
REQUEST_LATENCY = Histogram(
    'http_request_duration_seconds',
    'API Latency',
    ['method', 'endpoint']
)
HTTP_ERRORS_TOTAL = Counter(
    'http_errors_total',
    'Total number of API errors (4xx, 5xx)',
    ['method', 'endpoint', 'status_code']
)
PROCESSED_CHARACTERS = Gauge(
    'app_processed_characters_count',
    'Total number of characters stored in the local DB'
)

# --- 2. MIDDLEWARE FOR AUTOMATIC METRIC COLLECTION ---
# (Middleware remains the same)
async def metrics_middleware(request: Request, call_next):
    start_time = time.time()
    try:
        response = await call_next(request)
    except Exception as exc:
        HTTP_ERRORS_TOTAL.labels(
            method=request.method,
            endpoint=request.url.path,
            status_code=500
        ).inc()
        raise exc
    process_time = time.time() - start_time
    REQUEST_LATENCY.labels(
        method=request.method,
        endpoint=request.url.path
    ).observe(process_time)
    if response.status_code >= 400:
         HTTP_ERRORS_TOTAL.labels(
            method=request.method,
            endpoint=request.url.path,
            status_code=response.status_code
        ).inc()
    return response

# --- 3. EXPOSURE ---
def setup_metrics(app):
    """Adds the /metrics endpoint and the middleware to the FastAPI app."""
    app.middleware("http")(metrics_middleware)

    @app.get("/metrics")
    def get_metrics():
        # CORRECT WAY: Use generate_latest to get the metrics data
        return Response(
            content=generate_latest(REGISTRY), # Use generate_latest here
            media_type="text/plain"
        )
