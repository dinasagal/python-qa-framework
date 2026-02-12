import pytest

from pages.login_page import LoginPage


EMAIL = "ngjipiqmftuoxbkecx@nespj.com"
PASSWORD = "123456"


@pytest.mark.smoke
def test_successful_login(page):
    login = LoginPage(page)

    login.open_home()

    login.login(EMAIL, PASSWORD)
    login.wait_until_logged_in(EMAIL)

    assert login.is_auth_section_hidden()
    assert login.is_tasks_section_visible()
    assert EMAIL in login.get_user_email_text()
    assert login.is_auth_error_hidden()
