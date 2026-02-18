from datetime import datetime

from core.base_page import BasePage
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError


class FamilyAppPage(BasePage):
    #URL = "https://dinasagal.github.io/"
    URL = "http://localhost:5500/index.html"

    AUTH_SECTION = "#auth-section"
    TASKS_SECTION = "#tasks-section"
    CALENDAR_SECTION = "#calendar-section"
    MESSAGES_SECTION = "#messages-section"
    FAMILY_SETTINGS_SECTION = "#family-settings-section"

    SIDEBAR = "#sidebar"
    USER_EMAIL = "#user-email"
    SIDEBAR_LOGOUT = "#sidebar-logout"
    AUTH_PANEL_LOGOUT = "#logout-btn"
    NAV_SETTINGS = "#nav-settings"

    LOGIN_EMAIL = "#login-form input[name='email']"
    LOGIN_PASSWORD = "#login-form input[name='password']"
    LOGIN_BUTTON = "#login-form button[type='submit']"

    FAMILY_PANEL = "#family-panel"
    FAMILY_NAME = "#family-name"
    CREATE_FAMILY_SECTION = "#create-family-section"
    CREATE_FAMILY_FORM = "#create-family-form"
    CREATE_FAMILY_NAME_INPUT = "#create-family-form input[name='familyName']"

    ADD_CHILD_FORM = "#add-child-form"
    CHILD_EMAIL = "#add-child-form input[name='childEmail']"
    CHILD_PASSWORD = "#add-child-form input[name='childPassword']"
    CHILD_NAME = "#add-child-form input[name='childName']"
    PARENT_PASSWORD = "#add-child-form input[name='parentPassword']"
    FAMILY_MEMBERS_SECTION = "#family-members-section"
    SETTINGS_FAMILY_NAME = "#settings-family-name"
    FAMILY_MEMBERS_LIST = "#family-members-list"

    NEW_TASK_BUTTON = "#new-task-btn"
    TASK_FORM = "#task-form"
    TASK_TITLE = "#task-form input[name='title']"
    TASK_DETAILS = "#task-form textarea[name='content']"
    TASK_DUE_DATE = "#task-form input[name='dueDate']"
    TASK_ASSIGNEE_SELECT = "#assigned-user"
    TASK_SAVE_BUTTON = "#task-form button[type='submit']"
    TASKS_LIST = "#tasks-list"
    ARCHIVE_TOGGLE = "#archive-toggle"
    ARCHIVE_SECTION = "#archive-section"
    ARCHIVE_LIST = "#archive-list"

    NAV_TASKS = "a.nav-link[data-section='tasks']"
    NAV_CALENDAR = "a.nav-link[data-section='calendar']"
    NAV_MESSAGES = "a.nav-link[data-section='messages']"
    NAV_SETTINGS_SELECTOR = "a.nav-link[data-section='settings']"

    CALENDAR_DAYS = "#calendar-days-container"
    EVENT_MODAL = "#event-modal"
    EVENT_FORM = "#event-form"
    EVENT_TITLE = "#event-title"
    EVENT_DATE = "#event-date"
    EVENT_TIME = "#event-time"

    MESSAGE_FORM = "#message-form"
    MESSAGE_TEXT = "#message-text"
    MESSAGES_LIST = "#messages-list"

    def open_home(self):
        self.open(self.URL)
        self.page.wait_for_selector(self.AUTH_SECTION, state="visible")

    def login(self, email, password):
        self.page.wait_for_selector(self.LOGIN_EMAIL, state="visible")
        self.fill(self.LOGIN_EMAIL, email)
        self.fill(self.LOGIN_PASSWORD, password)
        self.click(self.LOGIN_BUTTON)

    def wait_until_logged_in(self, email):
        self.page.wait_for_selector(self.TASKS_SECTION, state="visible")
        self.page.wait_for_selector(self.SIDEBAR, state="visible")
        self.page.wait_for_function(
            """({ selector, expectedEmail }) => {
                const el = document.querySelector(selector);
                return Boolean(el) && el.textContent.includes(expectedEmail);
            }""",
            arg={"selector": self.USER_EMAIL, "expectedEmail": email},
        )

    def wait_until_logged_out(self):
        self.page.wait_for_selector(self.AUTH_SECTION, state="visible")
        self.page.wait_for_selector(self.TASKS_SECTION, state="hidden")

    def logout(self):
        sidebar_logout = self.page.locator(self.SIDEBAR_LOGOUT)
        auth_panel_logout = self.page.locator(self.AUTH_PANEL_LOGOUT)

        if sidebar_logout.count() > 0 and sidebar_logout.first.is_visible():
            sidebar_logout.first.click()
        elif auth_panel_logout.count() > 0 and auth_panel_logout.first.is_visible():
            auth_panel_logout.first.click()
        else:
            raise AssertionError("No logout control is visible in UI.")

        self.wait_until_logged_out()

    def switch_user_via_ui(self, email, password):
        self.logout()
        self.login(email, password)
        self.wait_until_logged_in(email)

    def open_tasks(self):
        self.page.locator(self.NAV_TASKS).click()
        self.page.wait_for_selector(self.TASKS_SECTION, state="visible")

    def open_calendar(self):
        self.page.locator(self.NAV_CALENDAR).click()
        self.page.wait_for_selector(self.CALENDAR_SECTION, state="visible")

    def open_messages(self):
        self.page.locator(self.NAV_MESSAGES).click()
        self.page.wait_for_selector(self.MESSAGES_SECTION, state="visible")

    def open_family_settings(self):
        self.page.locator(self.NAV_SETTINGS_SELECTOR).click()
        self.page.wait_for_selector(self.FAMILY_SETTINGS_SECTION, state="visible")

    def is_tasks_section_visible(self):
        return self.page.locator(self.TASKS_SECTION).is_visible()

    def is_sidebar_visible(self):
        return self.page.locator(self.SIDEBAR).is_visible()

    def is_family_panel_visible(self):
        return self.page.locator(self.FAMILY_PANEL).is_visible()

    def get_family_name_text(self):
        text = self.page.locator(self.FAMILY_NAME).text_content()
        return (text or "").strip()

    def is_create_family_visible(self):
        section = self.page.locator(self.CREATE_FAMILY_SECTION)
        return section.count() > 0 and section.first.is_visible()

    def create_family(self, family_name):
        self.page.wait_for_selector(self.CREATE_FAMILY_FORM, state="visible")
        self.fill(self.CREATE_FAMILY_NAME_INPUT, family_name)
        self.page.locator(f"{self.CREATE_FAMILY_FORM} button[type='submit']").click()
        self.page.wait_for_selector(self.FAMILY_PANEL, state="visible")

    def is_family_settings_nav_visible(self):
        nav = self.page.locator(self.NAV_SETTINGS)
        return nav.count() > 0 and nav.first.is_visible()

    def is_family_settings_section_visible(self):
        section = self.page.locator(self.FAMILY_SETTINGS_SECTION)
        return section.count() > 0 and section.first.is_visible()

    def is_family_members_section_visible(self):
        section = self.page.locator(self.FAMILY_MEMBERS_SECTION)
        return section.count() > 0 and section.first.is_visible()

    def get_settings_family_name_text(self):
        name = self.page.locator(self.SETTINGS_FAMILY_NAME)
        if name.count() == 0:
            return ""
        text = name.first.text_content()
        return (text or "").strip()

    def wait_for_settings_family_name(self, timeout=15000):
        try:
            self.page.wait_for_function(
                """({ selector }) => {
                    const el = document.querySelector(selector);
                    if (!el) return false;
                    const text = (el.textContent || '').trim();
                    return text !== '' && text !== '—';
                }""",
                arg={"selector": self.SETTINGS_FAMILY_NAME},
                timeout=timeout,
            )
        except PlaywrightTimeoutError:
            return ""
        return self.get_settings_family_name_text()

    def add_child_user(self, child_email, child_password, parent_password, child_name=""):
        self.page.wait_for_selector(self.ADD_CHILD_FORM, state="visible")
        self.fill(self.CHILD_EMAIL, child_email)
        self.fill(self.CHILD_PASSWORD, child_password)
        self.fill(self.CHILD_NAME, child_name)
        self.fill(self.PARENT_PASSWORD, parent_password)
        self.page.locator(f"{self.ADD_CHILD_FORM} button[type='submit']").click()
        self.page.wait_for_selector(self.FAMILY_MEMBERS_LIST, state="visible")

        expected_markers = [child_email]
        cleaned_name = (child_name or "").strip()
        if cleaned_name and cleaned_name != "—":
            expected_markers.insert(0, cleaned_name)

        try:
            self.page.wait_for_function(
                """({ selector, expected }) => {
                    const element = document.querySelector(selector);
                    if (!element) return false;
                    return expected.some((token) => token && element.textContent.includes(token));
                }""",
                arg={"selector": self.FAMILY_MEMBERS_LIST, "expected": expected_markers},
                timeout=25000,
            )
            return
        except PlaywrightTimeoutError:
            self.open_family_settings()
            self.page.wait_for_selector(self.FAMILY_MEMBERS_LIST, state="visible")

        try:
            self.page.wait_for_function(
                """({ selector, expected }) => {
                    const element = document.querySelector(selector);
                    if (!element) return false;
                    return expected.some((token) => token && element.textContent.includes(token));
                }""",
                arg={"selector": self.FAMILY_MEMBERS_LIST, "expected": expected_markers},
                timeout=20000,
            )
        except PlaywrightTimeoutError:
            auth_error = (self.page.locator("#auth-error").text_content() or "").strip()
            status_text = (self.page.locator("#status").text_content() or "").strip()
            details = auth_error or status_text or "Child did not appear in family list within timeout."
            raise AssertionError(f"Child creation not confirmed in UI for '{child_email}'. UI details: {details}")

    def is_family_member_listed(self, member_text):
        return self.page.locator(self.FAMILY_MEMBERS_LIST).inner_text().find(member_text) != -1

    def create_task(self, title, assigned_member_text=None, details=""):
        self.open_tasks()
        self.page.wait_for_selector(self.NEW_TASK_BUTTON, state="visible")
        self.page.locator(self.NEW_TASK_BUTTON).click()
        self.page.wait_for_selector(self.TASK_FORM, state="visible")

        self.fill(self.TASK_TITLE, title)
        self.fill(self.TASK_DETAILS, details)

        if assigned_member_text:
            option = self.page.locator(f"{self.TASK_ASSIGNEE_SELECT} option", has_text=assigned_member_text).first
            if option.count() == 0:
                raise AssertionError(f"No assignee option found for: {assigned_member_text}")
            value = option.get_attribute("value")
            if not value:
                raise AssertionError(f"Selected assignee option has no value: {assigned_member_text}")
            self.page.locator(self.TASK_ASSIGNEE_SELECT).select_option(value=value)

        self.page.locator(self.TASK_SAVE_BUTTON).click()
        self.page.wait_for_selector(self.TASKS_LIST, state="visible")
        self.page.wait_for_function(
            """({ selector, taskTitle }) => {
                const cards = Array.from(document.querySelectorAll(selector));
                return cards.some((card) => card.textContent.includes(taskTitle));
            }""",
            arg={"selector": "#tasks-list .task-card", "taskTitle": title},
        )

    def _task_card_locator(self, title, in_archive=False):
        list_selector = self.ARCHIVE_LIST if in_archive else self.TASKS_LIST
        return self.page.locator(f"{list_selector} .task-card", has_text=title).first

    def is_open_task_visible(self, title):
        card = self._task_card_locator(title, in_archive=False)
        return card.count() > 0 and card.is_visible()

    def is_archive_task_visible(self, title):
        card = self._task_card_locator(title, in_archive=True)
        return card.count() > 0 and card.is_visible()

    def get_task_card_text(self, title, in_archive=False):
        card = self._task_card_locator(title, in_archive=in_archive)
        if card.count() == 0:
            raise AssertionError(f"Task card not found for title: {title}")
        return card.inner_text()

    def complete_open_task(self, title):
        card = self._task_card_locator(title, in_archive=False)
        if card.count() == 0:
            raise AssertionError(f"Open task not found for completion: {title}")

        checkbox = card.locator("input[type='checkbox']").first
        if checkbox.count() == 0:
            raise AssertionError(f"Completion checkbox not found for task: {title}")
        checkbox.check(force=True)
        card.wait_for(state="hidden")

    def refresh_and_wait_user(self, email):
        self.page.reload(wait_until="domcontentloaded")
        self.wait_until_logged_in(email)

    def open_archive(self):
        self.open_tasks()
        if self.page.locator(self.ARCHIVE_SECTION).is_hidden():
            self.page.locator(self.ARCHIVE_TOGGLE).click()
        self.page.wait_for_selector(self.ARCHIVE_SECTION, state="visible")

    def wait_for_archive_task(self, title, timeout=45000):
        self.open_archive()
        try:
            self.page.wait_for_function(
                """({ title }) => {
                    const cards = Array.from(document.querySelectorAll('#archive-list .task-card'));
                    return cards.some((card) => card.textContent.includes(title));
                }""",
                arg={"title": title},
                timeout=timeout,
            )
            return True
        except PlaywrightTimeoutError:
            return False

    def create_calendar_event(self, title):
        self.open_calendar()

        calendar_user_select = self.page.locator("#calendar-user-select")
        if calendar_user_select.count() > 0:
            option_count = calendar_user_select.locator("option").count()
            if option_count > 0:
                first_value = calendar_user_select.locator("option").first.get_attribute("value")
                if first_value:
                    calendar_user_select.select_option(value=first_value)

        self.page.wait_for_function(
            """() => {
                const days = document.querySelectorAll('#calendar-days-container .calendar-day:not(.other-month)');
                return days.length > 0;
            }""",
            timeout=20000,
        )

        day_locator = self.page.locator("#calendar-days-container .calendar-day:not(.other-month)").first
        if day_locator.count() == 0:
            raise AssertionError("No clickable day cell found in calendar grid.")
        day_locator.click()

        self.page.wait_for_selector(self.EVENT_MODAL, state="visible")
        self.fill(self.EVENT_TITLE, title)

        today_iso = datetime.now().strftime("%Y-%m-%d")
        self.fill(self.EVENT_DATE, today_iso)
        self.fill(self.EVENT_TIME, "")

        self.page.locator(f"{self.EVENT_FORM} button[type='submit']").click()
        self.page.wait_for_selector(self.EVENT_MODAL, state="hidden")
        self.page.wait_for_function(
            """(title) => {
                const events = Array.from(document.querySelectorAll('.calendar-event'));
                return events.some((eventEl) => eventEl.textContent.includes(title));
            }""",
            arg=title,
        )

    def is_calendar_event_visible(self, title):
        return self.page.locator(".calendar-event", has_text=title).count() > 0

    def post_message(self, text):
        self.open_messages()
        self.page.wait_for_selector(self.MESSAGE_FORM, state="visible")
        self.fill(self.MESSAGE_TEXT, text)
        self.page.locator(f"{self.MESSAGE_FORM} button[type='submit']").click()
        self.page.wait_for_function(
            """({ selector, text }) => {
                const container = document.querySelector(selector);
                return Boolean(container) && container.textContent.includes(text);
            }""",
            arg={"selector": self.MESSAGES_LIST, "text": text},
        )

    def message_exists(self, text):
        return self.page.locator(self.MESSAGES_LIST).inner_text().find(text) != -1

    def open_direct_settings_url(self):
        self.open(f"{self.URL}#settings/add-member")
        self.page.wait_for_load_state("domcontentloaded")

    def is_add_child_form_visible(self):
        form = self.page.locator(self.ADD_CHILD_FORM)
        return form.count() > 0 and form.first.is_visible()
