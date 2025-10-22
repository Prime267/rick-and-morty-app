# --- EXTERNAL API CONFIG ---
EXTERNAL_API_URL = "https://rickandmortyapi.com/api/character"
EXTERNAL_FILTERS = {
    "species": "Human",
    "status": "Alive",
    # Origin filtering will be handled in code due to API limitations
}

# --- DATABASE CONFIG ---
# Load secrets from environment variables (K8s best practice)
DB_USER = os.getenv("DB_USER", "user")
DB_PASSWORD = os.getenv("DB_PASSWORD", "password")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_NAME = os.getenv("DB_NAME", "rickandmorty")

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"
