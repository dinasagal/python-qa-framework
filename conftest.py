from multiprocessing import context
import pytest
import os
import uuid
import allure
from playwright.sync_api import sync_playwright
from pages.login_page import LoginPage


@pytest.fixture(scope="session")
def browser():
    # GitHub Actions automatically sets CI=true
    is_ci = os.getenv("CI") == "true"

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=is_ci, slow_mo=0 if is_ci else 200)
        yield browser
        browser.close()


@pytest.fixture
def page(browser):
    context = browser.new_context()
    page = context.new_page()
    page.on("console", lambda msg: print("BROWSER LOG:", msg.type, msg.text))
    page.on("pageerror", lambda exc: print("PAGE ERROR:", exc))
    yield page
    context.close()


@pytest.fixture(scope="session")
def user_credentials_map():
    return {
        "default": {
            "email": os.getenv("UI_USER_DEFAULT_EMAIL", os.getenv("UI_TEST_EMAIL", "ngjipiqmftuoxbkecx@nespj.com")),
            "password": os.getenv("UI_USER_DEFAULT_PASSWORD", os.getenv("UI_TEST_PASSWORD", "123456")),
            "role": os.getenv("UI_USER_DEFAULT_ROLE", "parent"),
        },
        "child_1": {
            "email": os.getenv("UI_USER_CHILD1_EMAIL", ""),
            "password": os.getenv("UI_USER_CHILD1_PASSWORD", ""),
            "role": os.getenv("UI_USER_CHILD1_ROLE", "child"),
        },
        "child_2": {
            "email": os.getenv("UI_USER_CHILD2_EMAIL", ""),
            "password": os.getenv("UI_USER_CHILD2_PASSWORD", ""),
            "role": os.getenv("UI_USER_CHILD2_ROLE", "child"),
        },
    }


@pytest.fixture
def ui_user(request, user_credentials_map):
    user_key = getattr(request, "param", "default")
    if user_key not in user_credentials_map:
        raise ValueError(f"Unknown ui user profile: {user_key}")
    return user_credentials_map[user_key]


@pytest.fixture(scope="session")
def ui_auth_credentials(user_credentials_map):
    return {
        "email": user_credentials_map["default"]["email"],
        "password": user_credentials_map["default"]["password"],
    }


@pytest.fixture
def authenticated_user(page, ui_user):
    if not ui_user["email"] or not ui_user["password"]:
        raise ValueError("UI user credentials are missing. Set environment variables for the selected user profile.")

    login_page = LoginPage(page)
    with allure.step(f"Login as user: {ui_user['email']}"):
        login_page.open_home()
        login_page.login(ui_user["email"], ui_user["password"])
        login_page.wait_until_logged_in(ui_user["email"])

    yield {
        "page": page,
        "login_page": login_page,
        "user": ui_user,
        "email": ui_user["email"],
    }

    if login_page.is_tasks_section_visible():
        with allure.step("Logout in fixture teardown"):
            login_page.logout()


@pytest.fixture
def test_data_factory():
    def _build(prefix="qa"):
        token = uuid.uuid4().hex[:8]
        return {
            "name": f"{prefix}_{token}",
            "email": f"{prefix}_{token}@example.com",
            "title": f"{prefix}_task_{token}",
        }

    return _build

import os
import datetime
import pytest


def pytest_configure(config):
    """
    Runs before any test session starts.
    We override the allure results directory dynamically.
    """

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    results_dir = f"allure-results-{timestamp}"

    # store for later usage (optional)
    config.option.allure_report_dir = results_dir

    # tell allure where to write results
    os.environ["ALLURE_RESULTS_DIR"] = results_dir

    print(f"\nAllure results will be saved to: {results_dir}\n")


