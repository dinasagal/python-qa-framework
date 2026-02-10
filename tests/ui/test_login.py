from pages.login_page import LoginPage


def test_successful_login(page):
    login = LoginPage(page)

    login.open("https://www.saucedemo.com/")

    login.login("standard_user", "secret_sauce")

    assert "inventory" in page.url
