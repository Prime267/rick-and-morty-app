import os
from sqlalchemy import create_engine, Column, Integer, String, Boolean, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base

# Load constants (assuming constants.py is created in the root or accessible)
from .constants import DATABASE_URL 

# --- 1. BASE DECLARATION AND ENGINE SETUP ---
Base = declarative_base()

# The engine manages connections to the database.
engine = create_engine(DATABASE_URL)

# SessionLocal is the class for creating new session objects.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# --- 2. DATA MODEL: Character Table ---
class Character(Base):
    """
    SQLAlchemy model for persisting character data (Durability requirement).
    """
    __tablename__ = "characters"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    species = Column(String)
    status = Column(String)
    origin_name = Column(String)
    is_earth_origin = Column(Boolean) # Flag to simplify filtering logic (SRE efficiency)


# --- 3. SRE HELPER FUNCTIONS ---

def check_db_connection() -> bool:
    """
    Checks for an active database connection. 
    This is CRITICAL for the /healthcheck endpoint and the K8s Readiness Probe.
    """
    try:
        # Attempt a simple query execution to confirm the DB is responsive
        db: Session = SessionLocal()
        # Using text() ensures compatibility with raw SQL execution
        db.execute(text("SELECT 1")) 
        db.close()
        return True
    except Exception as e:
        print(f"Database connection check failed: {e}")
        return False


def init_db():
    """
    Creates the database tables if they do not already exist.
    Called once during application startup.
    """
    Base.metadata.create_all(bind=engine)

def get_db():
    """
    Dependency injection function to manage database sessions (FastAPI best practice).
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()