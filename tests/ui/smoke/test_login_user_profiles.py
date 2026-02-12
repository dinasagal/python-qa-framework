import os

import pytest


def _child1_credentials_configured():
    return bool(os.getenv("UI_USER_CHILD1_EMAIL") and os.getenv("UI_USER_CHILD1_PASSWORD"))

@pytest.mark.smoke
@pytest.mark.parametrize("ui_user", ["child_1"], indirect=True)
@pytest.mark.skipif(
    not _child1_credentials_configured(),
    reason="Set UI_USER_CHILD1_EMAIL and UI_USER_CHILD1_PASSWORD to run child_1 login.",
)
def test_successful_login_child1_user(authenticated_user):
    login = authenticated_user["login_page"]
    email = authenticated_user["email"]

    assert login.is_auth_section_hidden()
    assert login.is_tasks_section_visible()
    assert email in login.get_user_email_text()
    assert login.is_auth_error_hidden()
    assert authenticated_user["user"]["role"] == "child"
