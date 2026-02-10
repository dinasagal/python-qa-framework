import pytest
from playwright.sync_api import sync_playwright
from core.api_client import APIClient


@pytest.fixture(scope="session")
def browser():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        yield browser
        browser.close()


@pytest.fixture
def page(browser):
    context = browser.new_context()
    page = context.new_page()
    yield page
    context.close()


@pytest.fixture
def api_client():
    return APIClient("https://reqres.in/api")

