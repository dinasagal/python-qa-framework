from core.api_client import APIClient
import allure

@allure.feature("Users API")
@allure.story("Get users list")
def test_get_users(api_client):
    response = api_client.get("/users")
    assert response.status_code == 200

@allure.feature("Users API")
@allure.story("Create user")
def test_create_user(api_client, created_user):
    # user already created by fixture
    assert created_user is not None


@allure.feature("Users API")
@allure.story("Delete user")
def test_delete_user(api_client, created_user):
    response = api_client.delete(f"/users/{created_user}")
    assert response.status_code == 204

    verify = api_client.get(f"/users/{created_user}")
    assert verify.status_code == 404
