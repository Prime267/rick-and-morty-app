from prometheus_client import Gauge, Counter, Histogram, make_handler
from starlette.requests import Request
from starlette.responses import Response
import time

# --- 1. SRE METRICS DEFINITION ---

# Histogram: Measures request latency (Application-specific metric)
REQUEST_LATENCY = Histogram(
    'http_request_duration_seconds', 
    'API Latency',
    ['method', 'endpoint']
)

# Counter: Tracks API errors (Error Rates)
HTTP_ERRORS_TOTAL = Counter(
    'http_errors_total', 
    'Total number of API errors (4xx, 5xx)',
    ['method', 'endpoint', 'status_code']
)

# Gauge: Tracks business metric (Number of characters processed)
PROCESSED_CHARACTERS = Gauge(
    'app_processed_characters_count', 
    'Total number of characters stored in the local DB'
)

# --- 2. MIDDLEWARE FOR AUTOMATIC METRIC COLLECTION ---

async def metrics_middleware(request: Request, call_next):
    """
    Middleware to automatically measure latency and count errors for every request.
    """
    start_time = time.time()
    
    try:
        response = await call_next(request)
    except Exception as exc:
        # Increment global 500 error metric for unhandled exceptions
        HTTP_ERRORS_TOTAL.labels(
            method=request.method, 
            endpoint=request.url.path, 
            status_code=500
        ).inc()
        raise exc
        
    process_time = time.time() - start_time
    
    # Observe latency
    REQUEST_LATENCY.labels(
        method=request.method, 
        endpoint=request.url.path
    ).observe(process_time)

    # Count errors based on response status code (4xx or 5xx)
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
    
    # Add middleware for automatic collection
    app.middleware("http")(metrics_middleware)
    
    # Create the /metrics endpoint (required by Prometheus)
    @app.get("/metrics")
    def get_metrics():
        # Returns metrics in the plain text format required by Prometheus
        return Response(
            content=make_handler(), 
            media_type="text/plain"
        )
