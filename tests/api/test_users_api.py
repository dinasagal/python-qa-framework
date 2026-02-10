from core.api_client import APIClient


BASE_URL = "https://reqres.in/api"


def test_get_users(api_client):
    response = api_client.get("/users?page=2")

    assert response.status_code == 200
    assert "data" in response.json()


def test_create_user(api_client):
    payload = {
        "name": "Dina",
        "job": "QA Engineer"
    }

    response = api_client.post("/users", payload)

    assert response.status_code == 201
    assert response.json()["name"] == "Dina"


def test_delete_user(api_client):
    response = api_client.delete("/users/2")

    assert response.status_code == 204
