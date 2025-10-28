import pytest
from app.database import Character # Needed to check data in the DB
from app import constants # Needed for mocking the URL

# This fixture will be automatically picked up from conftest.py
# It provides the 'client' and a clean DB for each test


# --- UNIT TESTS ---
# (Test isolated logic, often using mocks)

@pytest.mark.unit
def test_healthcheck_db_failure(client, mocker):
    """
    Unit test: 
    Checks /healthcheck when the DB is "down".
    We mock the 'check_db_connection' function to return False.
    """
    # Mock the return value of the DB check function to False
    mocker.patch("app.database.check_db_connection", return_value=False)
    
    response = client.get("/healthcheck")
    
    # Expect 503 Service Unavailable, as specified in main.py
    assert response.status_code == 503
    assert response.json() == {"detail": "Database Connection Failed"}


@pytest.mark.unit
def test_get_characters_invalid_sort(client):
    """
    Unit test: 
    Checks the validation of the sort parameter.
    """
    response = client.get("/api/v1/characters?sort_by=invalid_param")
    assert response.status_code == 400
    assert "Invalid sort_by parameter" in response.json()["detail"]


# --- INTEGRATION TESTS ---
# (Test how components work together, e.g., API + Test DB)

@pytest.mark.integration
def test_healthcheck_success(client):
    """
    Integration test: 
    Checks /healthcheck. Since 'client' provides a working 
    in-memory DB, this request should return 200 OK.
    """
    response = client.get("/healthcheck")
    assert response.status_code == 200
    assert response.json() == {"status": "OK", "db_status": "Healthy"}


@pytest.mark.integration
def test_full_sync_and_get_flow(client, mocker):
    """
    Integration test (End-to-End):
    1. Mocks the external "Rick and Morty" API.
    2. Calls our /sync endpoint to populate the DB.
    3. Calls /api/v1/characters to get the filtered data.
    4. Checks filtering, pagination, and sorting.
    """
    
    # --- 1. Data for mocking the external API ---
    
    # Page 1
    page1_data = {
        "info": {"next": "http://fake-api/page2"},
        "results": [
            # 1. Valid: Human, Alive, Earth
            {"id": 1, "name": "Rick Sanchez", "species": "Human", "status": "Alive", "origin": {"name": "Earth (C-137)"}},
            # 2. Invalid: Species
            {"id": 2, "name": "Alien Rick", "species": "Alien", "status": "Alive", "origin": {"name": "Earth (C-137)"}},
            # 3. Invalid: Status
            {"id": 3, "name": "Dead Rick", "species": "Human", "status": "Dead", "origin": {"name": "Earth (C-137)"}},
        ]
    }
    
    # Page 2 (pagination)
    page2_data = {
        "info": {"next": None}, # Last page
        "results": [
            # 4. Invalid: Origin
            {"id": 4, "name": "Mars Rick", "species": "Human", "status": "Alive", "origin": {"name": "Mars"}},
            # 5. Valid: Human, Alive, Earth (another variation)
            {"id": 5, "name": "Morty Smith", "species": "Human", "status": "Alive", "origin": {"name": "Earth (Replacement Dimension)"}},
        ]
    }

    # Set up the mock for app.main.resilient_request
    # It will return different data depending on the URL
    def mock_resilient_request(url: str):
        if url == constants.EXTERNAL_API_URL:
            return page1_data
        if url == "http://fake-api/page2":
            return page2_data
        raise ValueError(f"Unexpected URL called: {url}")

    mocker.patch("app.main.resilient_request", side_effect=mock_resilient_request)
    
    # --- 2. Call /sync ---
    response_sync = client.post("/sync")
    assert response_sync.status_code == 200
    # Out of 5 characters, only 2 (id: 1, id: 5) are valid
    assert response_sync.json() == {"message": "Data synced successfully: 2 characters processed"}
    
    # --- 3. Call /api/v1/characters (no sorting) ---
    response_get = client.get("/api/v1/characters")
    assert response_get.status_code == 200
    data = response_get.json()
    
    assert len(data) == 2 # Ensure filtering worked
    assert data[0]["name"] == "Rick Sanchez"
    assert data[1]["name"] == "Morty Smith"
    
    # --- 4. Check sorting ---
    response_sorted = client.get("/api/v1/characters?sort_by=name")
    data_sorted = response_sorted.json()
    
    assert data_sorted[0]["name"] == "Morty Smith" # M...
    assert data_sorted[1]["name"] == "Rick Sanchez" # R...

    
@pytest.mark.integration
def test_sync_upsert_logic(client, mocker):
    """
    Integration test:
    Checks that calling /sync again updates (UPSERTs) data, 
    rather than duplicating it.
    """
    # --- 1. First Sync ---
    initial_data = {
        "info": {"next": None},
        "results": [
            {"id": 1, "name": "Rick", "species": "Human", "status": "Alive", "origin": {"name": "Earth (C-137)"}}
        ]
    }
    mocker.patch("app.main.resilient_request", return_value=initial_data)
    client.post("/sync")
    
    # Check
    response_v1 = client.get("/api/v1/characters")
    assert len(response_v1.json()) == 1
    assert response_v1.json()[0]["name"] == "Rick"

    # --- 2. Second Sync (same data, but name changed) ---
    updated_data = {
        "info": {"next": None},
        "results": [
            {"id": 1, "name": "Old Rick", "species": "Human", "status": "Alive", "origin": {"name": "Earth (C-137)"}}
        ]
    }
    mocker.patch("app.main.resilient_request", return_value=updated_data)
    client.post("/sync")
    
    # --- 3. Check the result ---
    response_v2 = client.get("/api/v1/characters")
    data_v2 = response_v2.json()
    
    # The character count is the same (not 2)
    assert len(data_v2) == 1 
    # But the name has been updated
    assert data_v2[0]["name"] == "Old Rick"
