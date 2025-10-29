import os

# --- EXTERNAL API CONFIG ---
EXTERNAL_API_URL = "https://rickandmortyapi.com/api/character"
EXTERNAL_FILTERS = {
    "species": "Human",
    "status": "Alive",
    # Origin filtering will be handled in code due to API limitations
}

# --- DATABASE CONFIG ---
# 1. (Production Priority): Use the DATABASE_URL from the environment if it exists.
#    This will be injected by Kubernetes/Terraform.
DATABASE_URL = os.getenv("DATABASE_URL")

# 2. (Local Fallback): If it doesn't exist, fall back to a simple SQLite file.
#    This makes local manual testing easy (e.g., 'uvicorn app.main:app').
if not DATABASE_URL:
    print("WARNING: DATABASE_URL not set. Falling back to local 'sqlite:///./test.db'")
    DATABASE_URL = "sqlite:///./test.db"
