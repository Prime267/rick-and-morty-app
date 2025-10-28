from contextlib import asynccontextmanager  # <-- NEW: for lifespan

import requests
from fastapi import Depends, FastAPI, HTTPException, Query

# --- NEW: Imports for Rate Limiting ---
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
from sqlalchemy.orm import Session
from starlette.requests import Request
from starlette.responses import JSONResponse
from tenacity import retry, stop_after_attempt, wait_exponential

# Import necessary local modules
from app import constants, database, metrics_setup
from app.database import Character


# --- 1. LIFESPAN EVENT (Fixes DeprecationWarning) ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Code to run on application startup
    print("--- Application starting up... ---")
    database.init_db()
    print("--- Database initialized ---")

    yield # Application runs here

    # Code to run on application shutdown (if needed)
    print("--- Application shutting down... ---")


# --- 2. INITIALIZATION and SRE MIDDLEWARE ---

# --- NEW: Initialize Rate Limiter ---
limiter = Limiter(key_func=get_remote_address)

app = FastAPI(
    title="Rick & Morty SRE App",
    lifespan=lifespan  # <-- NEW: Modern way to handle startup/shutdown
)

# --- NEW: Register limiter with the app ---
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# 2.1. SRE: Initialize Prometheus Metrics and Middleware
metrics_setup.setup_metrics(app)

# Global Exception Handler
@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    # CRITICAL: Increment the global 500 error counter for observability
    metrics_setup.HTTP_ERRORS_TOTAL.labels(
        method=request.method,
        endpoint=request.url.path,
        status_code=500
    ).inc()
    print(f"Unhandled error: {exc}")
    # Return a generic 500 response
    return JSONResponse(status_code=500, content={"message": "Internal Server Error"})


# --- 3. SRE: DEEP HEALTH CHECK ---
@app.get("/healthcheck")
async def deep_health_check():
    """
    K8s Readiness Probe: Checks connectivity to critical dependencies (DB).
    If the DB fails (returns False), the 503 response will cause
    K8s to stop sending traffic to this pod.
    """
    if not database.check_db_connection():
        raise HTTPException(status_code=503, detail="Database Connection Failed")
    return {"status": "OK", "db_status": "Healthy"}


# --- 4. RESILIENCE: Retry Logic ---
@retry(stop=stop_after_attempt(5), wait=wait_exponential(multiplier=1, min=2, max=10))
def resilient_request(url: str) -> dict:
    """Makes a GET request with retry logic for transient failures (429/5xx)."""
    response = requests.get(url, params=constants.EXTERNAL_FILTERS, timeout=10)

    # Retry on 429 (Rate Limit) or 5xx (Server Error)
    if response.status_code >= 429:
        err_msg = f"External API failed with status {response.status_code}. Retrying..."
        raise Exception(err_msg)

    # Fail fast on other 4xx client errors
    response.raise_for_status()
    return response.json()


# --- 5. DATA INGESTION JOB ---
def ingest_all_characters(db: Session):
    """Collects all pages of filtered data from the external API and persists them."""
    next_url = constants.EXTERNAL_API_URL
    processed_count = 0
    while next_url:
        data = resilient_request(next_url)
        # Define Earth variants as per the task
        earth_origins = ["Earth (C-137)", "Earth (Replacement Dimension)"]

        for char_data in data.get('results', []):
            # Check for "Earth" in origin name
            is_earth = (char_data['origin']['name'].startswith('Earth') or
                        char_data['origin']['name'] in earth_origins)

            # Persist only if all filters match
            if (char_data['species'] == constants.EXTERNAL_FILTERS['species'] and
                char_data['status'] == constants.EXTERNAL_FILTERS['status'] and
                is_earth):

                # Use "Upsert" logic (Update or Insert)
                # FIX: Wrapped line to satisfy E501
                existing_char = db.query(Character).filter(
                    Character.id == char_data['id']
                ).first()

                if existing_char:
                    # Update
                    existing_char.name = char_data['name']
                    existing_char.status = char_data['status']
                    existing_char.origin_name = char_data['origin']['name']
                    existing_char.is_earth_origin = is_earth
                else:
                    # Insert
                    new_char = Character(
                        id=char_data['id'],
                        name=char_data['name'],
                        species=char_data['species'],
                        status=char_data['status'],
                        origin_name=char_data['origin']['name'],
                        is_earth_origin=is_earth
                    )
                    db.add(new_char)

                db.commit() # Commit per character (or batch)
                processed_count += 1

        next_url = data['info'].get('next') # Handle pagination

    # SRE Observability: Update the business metric
    metrics_setup.PROCESSED_CHARACTERS.set(processed_count)
    return processed_count


# --- 6. MAIN API ENDPOINT (/characters) ---
@app.get("/api/v1/characters")
@limiter.limit("20/minute")  # <-- NEW: Rate limit
async def get_characters(
    request: Request,  # <-- NEW: 'request' is required for the limiter
    sort_by: str = Query(None, description="Sort by 'name' or 'id'"),
    db: Session = Depends(database.get_db)
):
    """Serves the filtered list of characters from our local DB."""

    # 400 Error Handling for invalid parameters
    if sort_by and sort_by not in ["name", "id"]:
        metrics_setup.HTTP_ERRORS_TOTAL.labels(
            method="GET",
            endpoint="/api/v1/characters",
            status_code=400
        ).inc()
        detail_msg = "Invalid sort_by parameter. Use 'name' or 'id'."
        raise HTTPException(status_code=400, detail=detail_msg)

    # Query the DB using the pre-filtered, SRE-efficient flag
    query = db.query(Character).filter(
        Character.species == constants.EXTERNAL_FILTERS['species'],
        Character.status == constants.EXTERNAL_FILTERS['status'],
        # FIX: Replaced '== True' with implicit check (E712)
        Character.is_earth_origin
    )

    # Apply sorting
    if sort_by == 'name':
        query = query.order_by(Character.name)
    elif sort_by == 'id':
        query = query.order_by(Character.id)

    characters = query.all()
    return characters


# --- 7. DATA SYNC ENDPOINT ---
@app.post("/sync")
@limiter.limit("5/minute")  # <-- NEW: Stricter rate limit
async def sync_data(
    request: Request,  # <-- NEW: 'request' is required for the limiter
    db: Session = Depends(database.get_db)
):
    """Triggers a manual data synchronization from the external API."""
    characters_count = ingest_all_characters(db)
    # FIX: Wrapped line to satisfy E501
    return {
        "message": f"Data synced successfully: {characters_count} characters processed"
    }


# --- 8. STARTUP EVENT (REMOVED) ---
# Old @app.on_event("startup") block is now handled by 'lifespan'
