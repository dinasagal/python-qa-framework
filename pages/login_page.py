from core.base_page import BasePage


class LoginPage(BasePage):

    URL = "https://dinasagal.github.io/"

    AUTH_SECTION = "#auth-section"
    TASKS_SECTION = "#tasks-section"
    USER_EMAIL = "#user-email"
    AUTH_ERROR = "#auth-error"

    LOGIN_FORM = "#login-form"
    LOGIN_EMAIL = "#login-form input[name='email']"
    LOGIN_PASSWORD = "#login-form input[name='password']"
    LOGIN_BUTTON = "#login-form button[type='submit']"

    def open_home(self):
        self.open(self.URL)

    def login(self, email, password):
        self.fill(self.LOGIN_EMAIL, email)
        self.fill(self.LOGIN_PASSWORD, password)
        self.click(self.LOGIN_BUTTON)

    def wait_until_logged_in(self, email):
        self.page.wait_for_selector(self.TASKS_SECTION, state="visible")
        self.page.wait_for_function(
            """({ selector, expectedEmail }) => {
                const element = document.querySelector(selector);
                return Boolean(element) && element.textContent.includes(expectedEmail);
            }""",
            arg={"selector": self.USER_EMAIL, "expectedEmail": email},
        )

    def is_auth_section_hidden(self):
        return self.page.locator(self.AUTH_SECTION).is_hidden()

    def is_tasks_section_visible(self):
        return self.page.locator(self.TASKS_SECTION).is_visible()

    def get_user_email_text(self):
        return self.get_text(self.USER_EMAIL)

    def is_auth_error_hidden(self):
        return self.page.locator(self.AUTH_ERROR).is_hidden()
