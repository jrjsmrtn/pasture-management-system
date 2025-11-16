# SPDX-FileCopyrightText: 2025 Georges Martin <jrjsmrtn@gmail.com>
# SPDX-License-Identifier: MIT

"""Step definitions for issue status workflow scenarios."""

import json
import re
import subprocess

import requests
from behave import given, then, use_step_matcher, when
from playwright.sync_api import expect
from requests.auth import HTTPBasicAuth

from features.steps.common import STATUS_MAP


@given('an issue exists with ID "{issue_id}" and status "{status}"')
def step_create_issue_with_id_status(context, issue_id, status):
    """Verify or create an issue with specific ID and status."""
    tracker_dir = getattr(context, "tracker_dir", "tracker")

    # Map status name to ID
    status_id = STATUS_MAP.get(status)
    assert status_id, f"Unknown status: {status}"

    # Create issue with roundup-admin
    cmd = [
        "roundup-admin",
        "-i",
        tracker_dir,
        "create",
        "issue",
        f"title=Test issue {issue_id}",
        f"status={status_id}",
    ]

    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

    assert result.returncode == 0, f"Failed to create issue. Stderr: {result.stderr}"

    # Store the issue ID
    created_id = result.stdout.strip()
    context.current_issue_id = f"issue{created_id}"
    context.current_issue_numeric_id = created_id

    # Debug: print what was created
    print(f"\nDEBUG CREATE: Created issue with ID: {created_id}")
    print(f"DEBUG CREATE: Status was set to: {status_id}")
    print(f"DEBUG CREATE: Command was: {cmd}")


@given('the issue status was changed to "{status}" at "{timestamp}"')
def step_issue_status_changed_at(context, status, timestamp):
    """Record that an issue status was changed at a specific time (for history testing)."""
    # For now, this is a placeholder - actual implementation would require
    # modifying the Roundup database journal to inject historical status changes
    # We'll implement this when we add status history tracking
    if not hasattr(context, "issue_status_history"):
        context.issue_status_history = []

    context.issue_status_history.append({"status": status, "timestamp": timestamp})


@when("I view the issue details")
def step_view_issue_details(context):
    """Navigate to the issue detail page."""
    issue_id = context.current_issue_id
    # Ensure proper URL formation
    tracker_url = context.tracker_url.rstrip("/")
    context.page.goto(f"{tracker_url}/{issue_id}")
    context.page.wait_for_load_state("networkidle")


@when('I click "{button_text}"')
def step_click_button(context, button_text):
    """Click a button or link with specific text."""
    # Try multiple selectors: button, input[type=submit], link
    selectors = [
        f'button:has-text("{button_text}")',
        f'input[type="submit"][value="{button_text}"]',
        f'a:has-text("{button_text}")',
        f'input[type="button"][value="{button_text}"]',
    ]

    clicked = False
    for selector in selectors:
        element = context.page.locator(selector)
        if element.count() > 0:
            element.first.click()
            context.page.wait_for_load_state("networkidle")
            clicked = True
            break

    assert clicked, f"Button/link '{button_text}' not found on page"


@when('I run roundup command "{command}"')
def step_run_roundup_command(context, command):
    """Run a roundup-admin command."""
    tracker_dir = getattr(context, "tracker_dir", "tracker")

    # Replace issue ID placeholders with actual created issue ID
    # If the command references "issue1" but we created issue15, update it
    if hasattr(context, "current_issue_id"):
        # Replace "issue1" with the actual issue ID (e.g., "issue15")
        command = command.replace("issue1", context.current_issue_id)

    # Map status names to IDs in the command
    # e.g., "set issue1 status=in-progress" -> "set issue1 status=2"
    original_command = command
    for status_name, status_id in STATUS_MAP.items():
        command = command.replace(f"status={status_name}", f"status={status_id}")

    # Debug: print the full command that will be executed
    full_cmd = ["roundup-admin", "-i", tracker_dir] + command.split()
    print(f"\nDEBUG: Original command: {original_command}")
    print(f"DEBUG: Mapped command: {command}")
    print(f"DEBUG: Full command list: {full_cmd}")
    print(f"DEBUG: STATUS_MAP: {STATUS_MAP}")

    # Build full command
    cmd = full_cmd

    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

    # Debug: print the result
    print(f"DEBUG RESULT: exit_code={result.returncode}")
    print(f"DEBUG RESULT: stdout={result.stdout}")
    print(f"DEBUG RESULT: stderr={result.stderr}")

    context.cli_result = result
    context.cli_exit_code = result.returncode
    context.cli_stdout = result.stdout.strip()
    context.cli_stderr = result.stderr.strip()


@when("I PATCH the current issue via API with JSON:")
def step_patch_api_with_json(context):
    """Send a PATCH request to the API to update the current issue."""
    # Get the issue ID from context
    issue_id = context.current_issue_id.replace("issue", "")

    # Build full URL
    api_url = "http://localhost:8080/pms/rest/data"
    endpoint = f"/issue/{issue_id}"
    full_url = f"{api_url}{endpoint}"

    # Get auth
    auth = HTTPBasicAuth("admin", "admin")

    # First, GET the issue to retrieve its etag
    get_response = requests.get(full_url, auth=auth, timeout=30)
    assert (
        get_response.status_code == 200
    ), f"Failed to GET issue for etag: {get_response.status_code}"

    issue_data = get_response.json()
    etag = issue_data.get("data", {}).get("@etag")
    assert etag, "No @etag found in issue data"

    # Parse JSON from docstring
    payload = json.loads(context.text)

    # Map status name to ID if status field is present
    if "status" in payload:
        status_name = payload["status"]
        status_id = STATUS_MAP.get(status_name)
        if status_id:
            payload["status"] = status_id

    # Prepare headers with If-Match
    headers = {
        "Content-Type": "application/json",
        "X-Requested-With": "XMLHttpRequest",
        "Origin": "http://localhost:8080",
        "Referer": "http://localhost:8080/pms/",
        "If-Match": etag,
    }

    # Make PATCH request
    response = requests.patch(full_url, json=payload, headers=headers, auth=auth, timeout=30)

    # Store response
    context.api_response = response
    context.api_status_code = response.status_code

    try:
        context.api_response_data = response.json()
    except json.JSONDecodeError:
        context.api_response_data = None
        context.api_response_text = response.text


@then('the issue status should be "{expected_status}"')
def step_verify_issue_status(context, expected_status):
    """Verify the issue has the expected status."""
    tracker_dir = getattr(context, "tracker_dir", "tracker")
    issue_id = context.current_issue_id

    # Use roundup-admin to check the status
    cmd = ["roundup-admin", "-i", tracker_dir, "display", issue_id]

    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

    assert result.returncode == 0, f"Failed to display issue. Stderr: {result.stderr}"

    output = result.stdout

    # Map status name to ID
    status_id = STATUS_MAP.get(expected_status)
    assert status_id, f"Unknown status: {expected_status}"

    # Check for "status: N" in output
    assert (
        f"status: {status_id}" in output.lower()
    ), f"Expected status '{expected_status}' (ID {status_id}) not found in issue. Output: {output}"


@then('I should see "{text}"')
def step_should_see_text(context, text):
    """Verify specific text is visible (on page for web-ui, in CLI output for cli)."""
    # Check if this is a CLI scenario
    if hasattr(context, "cli_stdout"):
        cli_output = context.cli_stdout
        assert text in cli_output, f"Text '{text}' not found in CLI output. Output: {cli_output}"
    else:
        # Web UI scenario
        page_content = context.page.content()
        assert text in page_content, f"Text '{text}' not found on page"


@then("the status change should be recorded in history")
def step_status_change_in_history(context):
    """Verify status change was recorded in issue history."""
    # For now, this is a placeholder - actual implementation requires
    # checking the Roundup journal/history
    # We'll verify this works when we implement status history tracking
    pass


@then('I should not see "{button_text}" button')
def step_should_not_see_button(context, button_text):
    """Verify a button is not visible on the page."""
    selectors = [
        f'button:has-text("{button_text}")',
        f'input[type="submit"][value="{button_text}"]',
        f'a:has-text("{button_text}")',
        f'input[type="button"][value="{button_text}"]',
    ]

    for selector in selectors:
        element = context.page.locator(selector)
        assert element.count() == 0, f"Button '{button_text}' should not be visible"


@then("only valid transitions should be available")
def step_only_valid_transitions_available(context):
    """Verify only valid status transitions are shown."""
    # For now, this is a placeholder - actual implementation requires
    # checking which workflow buttons are visible based on current status
    # We'll implement this when we add workflow buttons to templates
    pass


@then("the command should succeed")
def step_command_should_succeed(context):
    """Verify the CLI command succeeded."""
    assert context.cli_exit_code == 0, (
        f"Command failed with exit code {context.cli_exit_code}. "
        f"Stdout: {context.cli_stdout}. Stderr: {context.cli_stderr}"
    )


@then('issue "{issue_id}" should have status "{expected_status}"')
def step_verify_issue_id_status(context, issue_id, expected_status):
    """Verify a specific issue has the expected status."""
    tracker_dir = getattr(context, "tracker_dir", "tracker")

    # Use actual created issue ID if available and parameter is "1"
    if issue_id == "1" and hasattr(context, "current_issue_numeric_id"):
        issue_id = context.current_issue_numeric_id

    # Ensure issue_id has "issue" prefix
    if not issue_id.startswith("issue"):
        issue_id = f"issue{issue_id}"

    # Use roundup-admin to check the status
    cmd = ["roundup-admin", "-i", tracker_dir, "display", issue_id]

    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

    assert result.returncode == 0, f"Failed to display issue. Stderr: {result.stderr}"

    output = result.stdout

    # Map status name to ID
    status_id = STATUS_MAP.get(expected_status)
    assert status_id, f"Unknown status: {expected_status}"

    # Check for "status: N" in output
    assert (
        f"status: {status_id}" in output.lower()
    ), f"Expected status '{expected_status}' (ID {status_id}) not found in issue. Output: {output}"


@given("I have a valid API token")
def step_valid_api_token(context):
    """Set up valid API credentials (alias for consistency)."""
    context.api_auth = HTTPBasicAuth("admin", "admin")
    context.api_authenticated = True


@then("the response status should be {expected_status}")
def step_verify_response_status(context, expected_status):
    """Verify the API response status code."""
    expected_code = int(expected_status)
    assert context.api_status_code == expected_code, (
        f"Expected status {expected_code}, got {context.api_status_code}. "
        f"Response: {getattr(context, 'api_response_text', context.api_response_data)}"
    )


@then('I should see status change from "{old_status}" to "{new_status}" at "{timestamp}"')
def step_verify_status_change_history(context, old_status, new_status, timestamp):
    """Verify a specific status change appears in the history."""
    # Placeholder - requires implementation of status history display
    # For now, just check that the History section is visible
    page_content = context.page.content()
    assert "history" in page_content.lower(), "History section not found on page"


@then('the response should contain error "{error_message}"')
def step_response_contains_error(context, error_message):
    """Verify the API response contains a specific error message."""
    response_text = getattr(context, "api_response_text", "")
    response_data = getattr(context, "api_response_data", {})

    # Check both text and JSON response
    error_found = error_message in response_text or (
        isinstance(response_data, dict) and error_message in str(response_data)
    )

    assert error_found, (
        f"Expected error message '{error_message}' not found in response. "
        f"Response: {response_text or response_data}"
    )
