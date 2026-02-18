import os
import uuid

import pytest

from pages.family_app_page import FamilyAppPage


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


@pytest.mark.regression
def test_family_lifecycle_ui_journey(page, ctx):
    """
    Stateful release-blocker sanity suite:
    Parent -> child creation -> user switching -> task lifecycle -> calendar -> messages -> permissions.
    This is intentionally one continuous journey (non-isolated flow).
    """
    app = FamilyAppPage(page)

    # Shared runtime data used across the full journey.
    creds = _get_parent_credentials()
    token = uuid.uuid4().hex[:8]
    child_display_name = f"Kid-{token}"
    reply_text = f"Child reply {token}"
    event_title = f"Sanity Event {token}"

    ctx.parent_email = creds["email"]
    ctx.parent_password = creds["password"]
    ctx.child_email = f"sanity.child.{token}@example.com"
    ctx.child_password = f"KidPass{token}"
    ctx.task_title = f"Sanity Task {token}"
    ctx.message_text = f"Family sanity message {token}"

    # 01 Parent Login
    print("Step 01: Parent login via UI")
    app.open_home()
    app.login(ctx.parent_email, ctx.parent_password)
    app.wait_until_logged_in(ctx.parent_email)
    assert app.is_tasks_section_visible(), "Parent should be redirected to Tasks section after login."
    assert app.is_sidebar_visible(), "Sidebar should be visible for logged-in parent."
    print("Parent logged in")

    # 02 Family Exists
    print("Step 02: Verify family panel and family settings visibility")
    app.open_family_settings()
    assert app.is_family_settings_section_visible(), "Family settings section should be visible for parent."
    assert app.is_family_members_section_visible(), "Family members section should be visible in Family Settings."
    settings_family_name = app.wait_for_settings_family_name()
    if settings_family_name in {"", "—"}:
        settings_family_name = app.get_family_name_text()
    assert settings_family_name not in {"", "—"}, "Family name should exist in UI family labels."
    print("Family exists and is visible")

    # 03 Add Child
    print("Step 03: Parent adds child user")
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

    # 04 Child Login
    print("Step 04: Switch user via UI logout/login to child")
    app.switch_user_via_ui(ctx.child_email, ctx.child_password)
    assert app.is_tasks_section_visible(), "Child should land on Tasks section after login."
    assert not app.is_family_settings_nav_visible(), "Child must not see Family Settings entry in sidebar."
    print("Child logged in with restricted sidebar")

    # 05 Parent Assigns Task
    print("Step 05: Switch back to parent and assign task to child")
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

    # 06 Child Completes Task
    print("Step 06: Child completes assigned task")
    app.switch_user_via_ui(ctx.child_email, ctx.child_password)
    assert app.is_open_task_visible(ctx.task_title), "Child should see assigned open task before completion."
    app.complete_open_task(ctx.task_title)
    app.refresh_and_wait_user(ctx.child_email)
    assert not app.is_open_task_visible(ctx.task_title), "Completed task should not remain in child's open task list."
    print("Task completed by child")

    # 07 Parent Archives Task (completed task visible in archive)
    print("Step 07: Parent verifies completed task in archive")
    app.switch_user_via_ui(ctx.parent_email, ctx.parent_password)
    assert app.wait_for_archive_task(ctx.task_title), "Parent archive should contain completed child task."
    archived_task_text = app.get_task_card_text(ctx.task_title, in_archive=True)
    assert (
        ctx.child_email in archived_task_text or child_display_name in archived_task_text
    ), "Archived task should preserve child assignment display."
    print("Parent verified archived task")

    # 08 Calendar Event
    print("Step 08: Parent creates calendar event")
    app.create_calendar_event(event_title)
    assert app.is_calendar_event_visible(event_title), "Newly created calendar event should appear in month grid."
    print("Calendar event created and visible")

    # 09 Recurring Event TBD - intentionally skipped per product requirement.
    print("Step 09: Recurring event validation skipped (TBD in product)")

    # 10 Message Board Post
    print("Step 10: Parent posts message on message board")
    app.post_message(ctx.message_text)
    assert app.message_exists(ctx.message_text), "Parent message should appear in message feed."
    print("Parent message posted")

    # 11 Child Reply
    print("Step 11: Child replies to parent message")
    app.switch_user_via_ui(ctx.child_email, ctx.child_password)
    app.post_message(reply_text)
    assert app.message_exists(ctx.message_text), "Parent message should remain visible to child."
    assert app.message_exists(reply_text), "Child reply should appear in message feed."
    print("Child reply visible together with parent message")

    # 12 Permission Enforcement
    print("Step 12: Child attempts direct access to add-member URL")
    app.open_direct_settings_url()
    assert not app.is_family_settings_nav_visible(), "Child direct navigation should not expose Family Settings sidebar link."
    assert not app.is_family_settings_section_visible(), "Child should not be able to view family settings section."
    assert not app.is_add_child_form_visible(), "Child should not be able to access add-child form."
    print("Child blocked from settings/add-member")
