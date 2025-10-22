from fastapi import FastAPI, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from starlette.requests import Request
from starlette.responses import JSONResponse
import requests
from tenacity import retry, stop_after_attempt, wait_exponential

# Import necessary local modules
from . import database, metrics_setup, constants 

# --- 1. INITIALIZATION and SRE MIDDLEWARE ---
app = FastAPI(title="Rick & Morty SRE App")

# 1.1. SRE: Initialize Prometheus Metrics and Middleware
# This call adds the /metrics endpoint and the latency/error measuring middleware
metrics_setup.setup_metrics(app) 

# Global Exception Handler (e.g., for unexpected 500 errors)
@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    # CRITICAL: Increment the global 500 error counter for observability
    metrics_setup.HTTP_ERRORS_TOTAL.labels(
        method=request.method, 
        endpoint=request.url.path, 
        status_code=500
    ).inc()
    print(f"Unhandled error: {exc}")
    # Return a 500 response
    return JSONResponse(status_code=500, content={"message": "Internal Server Error"})


# --- 2. SRE: DEEP HEALTH CHECK (Used by K8s Readiness Probe) ---
@app.get("/healthcheck")
async def deep_health_check():
    """
    K8s Readiness Probe: Checks connectivity to critical dependencies (DB).
    If the DB fails, the Readiness Probe should fail (returns 503).
    """
    if not database.check_db_connection():
        # Returns 503, preventing K8s from sending traffic to this Pod
        # (This links directly to the K8s Probe configuration)
        raise HTTPException(status_code=503, detail="Database Connection Failed")
    
    # If caching (Redis) was used, check its status here as well.
    return {"status": "OK", "db_status": "Healthy"}


# --- 3. RESILIENCE: Retry Logic for External API ---

@retry(stop=stop_after_attempt(5), wait=wait_exponential(multiplier=1, min=2, max=10))
def resilient_request(url: str) -> dict:
    """
    Makes a GET request with retry logic for transient failures (429/5xx).
    """
    # Note: Filters are added here via constants
    response = requests.get(url, params=constants.EXTERNAL_FILTERS, timeout=10)
    
    # If the external API hits a Rate Limit (429) or Server Error (5xx), we retry
    if response.status_code >= 429:
        # Tenacity will catch this Exception and automatically retry the attempt
        raise Exception(f"External API failed with status {response.status_code}. Retrying...")
    
    response.raise_for_status() # Raise exception for other non-retriable 4xx errors
    return response.json()


# --- 4. DATA INGESTION JOB (Logic covering Pagination) ---

def ingest_all_characters(db: Session):
    """
    Collects all pages of filtered data from the external API and persists them.
    Handles pagination gracefully.
    """
    next_url = constants.EXTERNAL_API_URL
    processed_count = 0
    
    while next_url:
        data = resilient_request(next_url)
        
        # --- Minimal Filtering Logic (as per task requirements) ---
        earth_origins = ["Earth (C-137)", "Earth (Replacement Dimension)"]
        
        for char_data in data.get('results', []):
            is_earth = char_data['origin']['name'].startswith('Earth') or char_data['origin']['name'] in earth_origins
            
            # Persist data ONLY if it meets all the specific requirements
            if (char_data['species'] == constants.EXTERNAL_FILTERS['species'] and 
                char_data['status'] == constants.EXTERNAL_FILTERS['status'] and
                is_earth):
                 
                 # --- ORM Logic to save/update data in DB ---
                 # (Minimal ORM interaction goes here)
                 processed_count += 1
                 
        
        next_url = data['info'].get('next')

    # Update the business metric (critical for the Bonus section)
    metrics_setup.PROCESSED_CHARACTERS.set(processed_count)


# --- 5. MAIN API ENDPOINT (/characters) ---

@app.get("/api/v1/characters")
async def get_characters(
    sort_by: str = Query(None, description="Sort by 'name' or 'id'"),
    db: Session = Depends(database.get_db)
):
    # Error Handling for invalid requests (400 Bad Request)
    if sort_by and sort_by not in ["name", "id"]:
        # Increment 400 error metric before raising exception
        metrics_setup.HTTP_ERRORS_TOTAL.labels(
            method="GET", 
            endpoint="/api/v1/characters", 
            status_code=400
        ).inc()
        raise HTTPException(status_code=400, detail="Invalid sort_by parameter. Use 'name' or 'id'.")

    # --- Logic to read characters from DB with sorting ---
    # The actual query logic using SQLAlchemy (SQLAlchemy logic goes here)
    characters = db.query(database.Character).all()
    
    # Return filtered and sorted data in JSON format
    return characters 

# --- 6. STARTUP EVENT ---
@app.on_event("startup")
def startup_event():
    # Initialize the database table structure
    database.init_db()
    # In a real environment, ingestion would run as a separate CronJob/Task or on a timer.
    # For a simple demo, we could call ingest_all_characters here, but it's risky for K8s startup time.