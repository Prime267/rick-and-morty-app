import os

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# 1. Import the *modules* themselves so we can patch them
from app import database, main

# 2. Define Test DB URL
# IMPORTANT: Override the production DATABASE_URL env var just in case
os.environ["DATABASE_URL"] = "sqlite:///:memory:"

# 3. Create the test engine
DATABASE_URL_TEST = "sqlite:///:memory:"

test_engine = create_engine(
    DATABASE_URL_TEST,
    # 'check_same_thread' is only needed for SQLite
    connect_args={"check_same_thread": False}
)

# 4. Create the test session
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


# 5. --- THIS IS THE MAGIC ---
# Monkey-patch the original engine and SessionLocal in the database module
# Now, any code in the app that imports 'engine' or 'SessionLocal'
# from 'app.database' will get our test versions.
database.engine = test_engine
database.SessionLocal = TestingSessionLocal
# -----------------------------


# 6. Get the app and Base *after* patching
app = main.app
Base = database.Base


# 7. Override the get_db dependency (still good practice)
def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[database.get_db] = override_get_db


# 8. The main "client" fixture
@pytest.fixture(scope="function")
def client():
    # We no longer need to mock init_db, because if it *did* run,
    # it would use our test_engine. But we still create tables manually.

    # Create all tables on the *test* engine
    Base.metadata.create_all(bind=test_engine)

    with TestClient(app) as test_client:
        yield test_client # The test runs here

    # Drop all tables from the *test* engine
    Base.metadata.drop_all(bind=test_engine)
