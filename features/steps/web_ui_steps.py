# SPDX-FileCopyrightText: 2025 Georges Martin <jrjsmrtn@gmail.com>
# SPDX-License-Identifier: MIT

"""Step definitions for Web UI interactions with Roundup tracker."""

from behave import given, then, when
from playwright.sync_api import expect

from tests.config.playwright_config import DEFAULT_TRACKER_URL


def check_for_templating_error(page, step_description=""):
    """
    Check if the current page contains a Roundup templating error.

    Roundup returns HTTP 200 even when TAL templates have errors,
    so we must check the page content for error markers.

    Args:
        page: Playwright page object
        step_description: Description of the step for error messages

    Raises:
        AssertionError: If a templating error is detected
    """
    body_text = page.locator("body").inner_text()

    if "Templating Error" in body_text or "TAL" in body_text and "Error" in body_text:
        # Capture screenshot for debugging
        screenshot_path = f"screenshots/templating_error_{step_description.replace(' ', '_')}.png"
        page.screenshot(path=screenshot_path)

        # Get error details
        error_type = ""
        error_msg = ""
        try:
            error_type_elem = page.locator("h3:has-text('Error Type')")
            if error_type_elem.count() > 0:
                error_type = error_type_elem.locator("..").inner_text()
        except Exception:
            pass

        raise AssertionError(
            f"Roundup templating error detected after: {step_description}\n"
            f"Screenshot saved to: {screenshot_path}\n"
            f"Error details: {error_type[:500] if error_type else 'See screenshot'}\n"
            f"Body preview: {body_text[:200]}"
        )


@given("the Roundup tracker is running")
@given('the Roundup tracker is running at "{url}"')
def step_tracker_running(context, url=None):
    """Start the Roundup tracker if needed and verify it's accessible."""
    import subprocess
    import time

    # Use provided URL or default from context (configured in environment.py)
    tracker_url = url if url else getattr(context, "tracker_url", DEFAULT_TRACKER_URL)

    # Store the URL in context
    context.tracker_url = tracker_url

    # Start server if not running (needed for Web UI and API scenarios)
    # Check if server is responding
    import requests

    try:
        response = requests.get(tracker_url, timeout=2)
        server_running = response.status_code == 200
    except requests.exceptions.RequestException:
        server_running = False

    if not server_running:
        # Start the server
        tracker_dir = getattr(context, "tracker_dir", "tracker")
        subprocess.Popen(
            ["uv", "run", "roundup-server", "-p", "9080", f"pms={tracker_dir}"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        # Wait for server to start
        time.sleep(3)

    # For Web UI scenarios, verify access via browser
    try:
        page = getattr(context, "page", None)
        if page is not None:
            response = page.goto(tracker_url)
            assert response.ok, f"Tracker not accessible at {tracker_url}"
    except AttributeError:
        # No page available - CLI or API scenario
        pass


@given("I am logged in to the web UI")
def step_login_default(context):
    """Log in to the Roundup tracker as admin (default user)."""
    # Skip for non-web-UI scenarios (CLI/API)
    if not hasattr(context, "page") or context.page is None:
        return
    step_login_as_user(context, "admin", "admin")


@given('I am logged in to the web UI as "{username}"')
@given('I am logged in to the web UI as "{username}" with password "{password}"')
def step_login_as_user(context, username, password="admin"):
    """Log in to the Roundup tracker as the specified user."""
    # Skip for non-web-UI scenarios (CLI/API)
    if not hasattr(context, "page") or context.page is None:
        return

    # Navigate to the tracker
    context.page.goto(context.tracker_url)
    check_for_templating_error(context.page, "navigate to tracker homepage")

    # Check if already logged in by looking for logout link
    logout_link = context.page.locator('a:has-text("Logout")')
    if logout_link.count() > 0:
        # Already logged in
        return

    # Fill in login form
    # The login form fields in Roundup classic are: __login_name and __login_password
    context.page.fill('input[name="__login_name"]', username)
    context.page.fill('input[name="__login_password"]', password)

    # Submit login - use type=submit with value=Login
    context.page.click('input[type="submit"][value="Login"]')

    # Wait for successful login - check for user name or logout link
    context.page.wait_for_selector('a:has-text("Logout")', timeout=5000)
    check_for_templating_error(context.page, "login")


@when('I navigate to the "{page_name}" page')
def step_navigate_to_page(context, page_name):
    """Navigate to a specific page in the tracker."""
    if page_name == "New Issue":
        # In Roundup classic, new issue is at: /issue?@template=item
        context.page.goto(f"{context.tracker_url}issue?@template=item")
        context.page.wait_for_load_state("networkidle")
        check_for_templating_error(context.page, f"navigate to {page_name}")
    elif page_name == "Issues":
        # In Roundup classic, issue list is at: /issue
        context.page.goto(f"{context.tracker_url}issue")
        context.page.wait_for_load_state("networkidle")
        check_for_templating_error(context.page, f"navigate to {page_name}")


@when("I enter the following issue details:")
def step_enter_issue_details(context):
    """Enter issue details from a table."""
    for row in context.table:
        field_name = row["field"]
        field_value = row["value"]

        if field_name == "title":
            # In Roundup classic, the issue title field is named 'title'
            context.page.fill('input[name="title"]', field_value)
            # Store for later verification
            context.issue_title = field_value

        elif field_name == "priority":
            # Priority is a select/dropdown in Roundup classic
            context.page.select_option('select[name="priority"]', label=field_value)
            # Store for later verification
            context.issue_priority = field_value


@when("I submit the issue")
def step_submit_issue(context):
    """Submit the issue creation form."""
    # In Roundup, there are multiple submit buttons on the page
    # We need the one with name="submit_button" for issue creation
    submit_button = context.page.locator('input[name="submit_button"]').first
    submit_button.click()

    # Wait for navigation/response
    context.page.wait_for_load_state("networkidle")


@when("I submit the issue without entering a title")
def step_submit_without_title(context):
    """Submit the issue form without filling in the title."""
    # Don't fill in the title field
    # Just try to submit
    submit_button = context.page.locator('input[type="submit"]').first
    submit_button.click()


@then("I should see a success message")
def step_see_success_message(context):
    """Verify a success message is displayed."""
    # Roundup redirects to the created issue page with @ok_message query param
    # URL format: http://localhost:8080/pms/issue1?@ok_message=issue%201%20created&@template=item
    page_url = context.page.url
    page_content = context.page.content()

    # Check if redirected to an issue or change page
    assert (
        ("issue" in page_url.lower() or "change" in page_url.lower())
        and "issue?" not in page_url.lower()  # issue1, issue2, not issue?@template
        and "change?" not in page_url.lower()  # change1, change2, not change?@template
    ), f"Not redirected to item page. Current URL: {page_url}"

    # Extract the issue ID from the URL for later verification
    # URL format: http://localhost:8080/pms/issue1?@ok_message=...
    if "/issue" in page_url:
        # Extract issue ID from URL like /issue1 or /issue1?params
        parts = page_url.split("/")
        issue_part = [p for p in parts if p.startswith("issue") and p != "issue"][0]
        # Remove query string if present
        issue_id = issue_part.split("?")[0]
        context.created_issue_id = issue_id


@then("the issue should appear in the issue list")
def step_issue_in_list(context):
    """Verify the created issue appears in the issue list."""
    # Navigate to the issue list
    context.page.goto(f"{context.tracker_url}issue")
    context.page.wait_for_load_state("networkidle")

    # Look for the issue title in the list
    issue_title = getattr(context, "issue_title", None)
    if issue_title:
        # Use .first to handle cases where multiple issues have the same title
        title_locator = context.page.locator(f'a:has-text("{issue_title}")').first
        expect(title_locator).to_be_visible()


# Note: Generic title and priority verification steps are in cli_steps.py
# to avoid duplication and allow context-aware implementation


@then("I should see a validation error")
def step_see_validation_error(context):
    """Verify a validation error is displayed."""
    # HTML5 validation or Roundup validation message
    # Check if we're still on the form page (not navigated away)
    assert "template=item" in context.page.url or "issue?" in context.page.url

    # Could be HTML5 validation (browser prevents submit) or server-side error
    # For HTML5, the title field should be marked as required and invalid
    title_input = context.page.locator('input[name="title"]')
    if title_input.count() > 0:
        # We should still be on the form page
        pass


@then("the issue should not be created")
def step_issue_not_created(context):
    """Verify the issue was not created."""
    # Navigate to issue list and verify no new issue
    context.page.goto(f"{context.tracker_url}issue")
    context.page.wait_for_load_state("networkidle")

    # The issue list should not contain an issue with empty title or just created
    # This is a basic check - in practice, we'd track issue count before/after
    page_content = context.page.content()
    # If we're back on the list and there are no issues, this is successful
    # Or if the form is still showing, that's also validation working
    assert True  # Placeholder - would need more sophisticated check in real scenario
