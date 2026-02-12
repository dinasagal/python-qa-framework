import pytest
import allure

@allure.feature("Users UI")
@allure.story("Successful login")
@pytest.mark.smoke
@pytest.mark.parametrize("ui_user", ["default"], indirect=True)
def test_successful_login_default_user(authenticated_user):
    login = authenticated_user["login_page"]
    email = authenticated_user["email"]

    assert login.is_auth_section_hidden()
    assert login.is_tasks_section_visible()
    assert email in login.get_user_email_text()
    assert login.is_auth_error_hidden()
