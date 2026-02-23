import os
import uuid
import pytest
import allure
from pages.family_app_page import FamilyAppPage

@allure.epic("Family App")
@allure.feature("End to End Lifecycle")
@allure.story("Parent Child Daily Usage")
@allure.severity(allure.severity_level.BLOCKER)
@allure.title("Family Lifecycle Sanity Journey")

class SanityContext:
    parent_email = None
    parent_password = None
    child_email = None
    child_password = None
    task_title = None
    message_text = None


@pytest.fixture(scope="module")
def ctx():
    return SanityContext()


def _get_parent_credentials():
    return {
        "email": os.getenv("UI_USER_DEFAULT_EMAIL", os.getenv("UI_TEST_EMAIL", "ngjipiqmftuoxbkecx@nespj.com")),
        "password": os.getenv("UI_USER_DEFAULT_PASSWORD", os.getenv("UI_TEST_PASSWORD", "123456")),
    }


def _prepare_runtime_context(ctx):
    creds = _get_parent_credentials()
    token = uuid.uuid4().hex[:8]

    ctx.parent_email = creds["email"]
    ctx.parent_password = creds["password"]
    ctx.child_email = f"sanity.child.{token}@example.com"
    ctx.child_password = f"KidPass{token}"
    ctx.task_title = f"Sanity Task {token}"
    ctx.message_text = f"Family sanity message {token}"

    return {
        "child_display_name": f"Kid-{token}",
        "reply_text": f"Child reply {token}",
        "event_title": f"Sanity Event {token}",
    }


def parent_login(app, ctx):
    with allure.step("01 Parent logs into the application"):
        app.open_home()
        app.login(ctx.parent_email, ctx.parent_password)
        app.wait_until_logged_in(ctx.parent_email)
        assert app.is_tasks_section_visible(), "Parent should be redirected to Tasks section after login."
        assert app.is_sidebar_visible(), "Sidebar should be visible for logged-in parent."
        print("Parent logged in")


def verify_family_exists(app):
    with allure.step("02 Verify family panel and family settings visibility"):
        app.open_family_settings()
        assert app.is_family_settings_section_visible(), "Family settings section should be visible for parent."
        assert app.is_family_members_section_visible(), "Family members section should be visible in Family Settings."
        settings_family_name = app.wait_for_settings_family_name()
        if settings_family_name in {"", "—"}:
            settings_family_name = app.get_family_name_text()
        assert settings_family_name not in {"", "—"}, "Family name should exist in UI family labels."
        print("Family exists and is visible")


def create_child(app, ctx, child_display_name):
    with allure.step("03 Parent adds child user"):
        app.add_child_user(
            child_email=ctx.child_email,
            child_password=ctx.child_password,
            parent_password=ctx.parent_password,
            child_name=child_display_name,
        )
        assert (
            app.is_family_member_listed(child_display_name) or app.is_family_member_listed(ctx.child_email)
        ), "New child should appear in family members list."
        print("Child created")


def child_login_and_verify_restrictions(app, ctx):
    with allure.step("04 Switch user via UI logout/login to child"):
        app.switch_user_via_ui(ctx.child_email, ctx.child_password)
        assert app.is_tasks_section_visible(), "Child should land on Tasks section after login."
        assert not app.is_family_settings_nav_visible(), "Child must not see Family Settings entry in sidebar."
        print("Child logged in with restricted sidebar")


def parent_assign_task(app, ctx, child_display_name):
    with allure.step("05 Switch back to parent and assign task to child"):
        app.switch_user_via_ui(ctx.parent_email, ctx.parent_password)
        app.create_task(
            title=ctx.task_title,
            assigned_member_text=ctx.child_email,
            details="Sanity E2E lifecycle task",
        )
        created_task_text = app.get_task_card_text(ctx.task_title)
        assert "Assigned:" in created_task_text, "Task card should show assignment metadata."
        assert (
            ctx.child_email in created_task_text or child_display_name in created_task_text
        ), "Task card should show child assignee identity."
        print("Task assigned to child")


def child_complete_task(app, ctx):
    with allure.step("Step 06 Child completes assigned task"):
        app.switch_user_via_ui(ctx.child_email, ctx.child_password)
        assert app.wait_for_open_task(ctx.task_title), "Child should see assigned open task before completion."
        allure.attach(
            app.get_ui_diagnostics(),
            name="Step06 pre-completion diagnostics",
            attachment_type=allure.attachment_type.TEXT,
        )

        attempts = 3
        for attempt in range(1, attempts + 1):
            with allure.step(f"Step 06 completion attempt {attempt}/{attempts}"):
                app.complete_open_task(ctx.task_title)
                app.refresh_and_wait_user(ctx.child_email)
                allure.attach(
                    app.get_ui_diagnostics(),
                    name=f"Step06 diagnostics after attempt {attempt}",
                    attachment_type=allure.attachment_type.TEXT,
                )

                if app.wait_for_task_not_open(ctx.task_title, timeout=15000):
                    break

                if attempt < attempts:
                    assert app.wait_for_open_task(ctx.task_title, timeout=20000), (
                        "Task did not settle between completion attempts. "
                        + app.get_ui_diagnostics()
                    )

        assert app.wait_for_task_not_open(ctx.task_title, timeout=15000), (
            "Completed task should not remain in child's open task list after retries. "
            + app.get_ui_diagnostics()
        )
        print("Task completed by child")


def parent_verify_archive(app, ctx, child_display_name):
    with allure.step("Step 07: Parent verifies completed task in archive"):
        app.switch_user_via_ui(ctx.parent_email, ctx.parent_password)
        assert app.wait_for_archive_task(ctx.task_title), "Parent archive should contain completed child task."
        archived_task_text = app.get_task_card_text(ctx.task_title, in_archive=True)
        assert (
            ctx.child_email in archived_task_text or child_display_name in archived_task_text
        ), "Archived task should preserve child assignment display."
        print("Parent verified archived task")


def parent_create_calendar_event(app, event_title):
    with allure.step("Step 08: Parent creates calendar event"):
        app.create_calendar_event(event_title)
        assert app.is_calendar_event_visible(event_title), "Newly created calendar event should appear in month grid."
        print("Calendar event created and visible")


def skip_recurring_event_tbd():
    with allure.step("Step 09: Recurring event validation skipped (TBD in product)"):
        print("Recurring event creation/validation skipped as per current product scope")


def parent_post_message(app, ctx):
    with allure.step("Step 10: Parent posts message on message board"):
        app.post_message(ctx.message_text)
        assert app.message_exists(ctx.message_text), "Parent message should appear in message feed."
        print("Parent message posted")


def child_reply_to_message(app, ctx, reply_text):
    with allure.step("Step 11: Child replies to parent message"):
        app.switch_user_via_ui(ctx.child_email, ctx.child_password)
        app.post_message(reply_text)
        assert app.message_exists(ctx.message_text), "Parent message should remain visible to child."
        assert app.message_exists(reply_text), "Child reply should appear in message feed."
        print("Child reply visible together with parent message")


def child_permission_enforcement(app):
    with allure.step("Step 12: Child attempts direct access to add-member URL"):
        app.open_direct_settings_url()
        assert not app.is_family_settings_nav_visible(), "Child direct navigation should not expose Family Settings sidebar link."
        assert not app.is_family_settings_section_visible(), "Child should not be able to view family settings section."
        assert not app.is_add_child_form_visible(), "Child should not be able to access add-child form."
        print("Child blocked from settings/add-member")


@pytest.mark.sanity
def test_family_lifecycle_ui_journey(page, ctx):
    """
    Stateful release-blocker sanity suite:
    Parent -> child creation -> user switching -> task lifecycle -> calendar -> messages -> permissions.
    This is intentionally one continuous journey (non-isolated flow).
    """
    app = FamilyAppPage(page)
    runtime = _prepare_runtime_context(ctx)
    child_display_name = runtime["child_display_name"]
    reply_text = runtime["reply_text"]
    event_title = runtime["event_title"]
    allure.attach(str(vars(ctx)), name="Sanity Context", attachment_type=allure.attachment_type.TEXT)

    parent_login(app, ctx)
    verify_family_exists(app)
    create_child(app, ctx, child_display_name)
    child_login_and_verify_restrictions(app, ctx)
    parent_assign_task(app, ctx, child_display_name)
    child_complete_task(app, ctx)
    parent_verify_archive(app, ctx, child_display_name)
    parent_create_calendar_event(app, event_title)
    skip_recurring_event_tbd()
    parent_post_message(app, ctx)
    child_reply_to_message(app, ctx, reply_text)
    child_permission_enforcement(app)
