import pytest
from playwright.sync_api import sync_playwright
from core.api_client import APIClient
import uuid

@pytest.fixture
def api_client():
    return APIClient("https://gorest.co.in/public/v2")

@pytest.fixture
def created_user(api_client):
    unique_email = f"dina_{uuid.uuid4()}@example.com"

    payload = {
        "name": "Dina QA",
        "gender": "female",
        "email": unique_email,
        "status": "active"
    }

    response = api_client.post("/users", payload)
    assert response.status_code == 201

    user_id = response.json()["id"]

    yield user_id

    # Teardown
    api_client.delete(f"/users/{user_id}")