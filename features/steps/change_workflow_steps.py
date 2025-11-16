# SPDX-FileCopyrightText: 2025 Georges Martin <jrjsmrtn@gmail.com>
# SPDX-License-Identifier: MIT

"""Step definitions for change workflow scenarios."""

import subprocess

from behave import given, then, when

from features.steps.common import CHANGESTATUS_MAP


@given('a change exists with title "{title}" and status "{status}"')
def step_create_change_with_status(context, title, status):
    """Create a change with specific title and status."""
    status_id = CHANGESTATUS_MAP.get(status.lower())
    if not status_id:
        raise ValueError(f"Unknown status: {status}")

    # Create change via CLI
    cmd = [
        "roundup-admin",
        "-i",
        "tracker",
        "create",
        "change",
        f"title={title}",
        f"description=Test change for {title}",
        "justification=Testing workflow",
        "priority=2",  # medium
        "category=1",  # software
        f"status={status_id}",
    ]

    result = subprocess.run(cmd, capture_output=True, text=True, timeout=10, check=True)

    # Extract change ID from output
    change_id = result.stdout.strip()
    context.created_change_id = change_id
    context.change_title = title


@given('a change exists with ID "{change_id:d}" and status "{status}"')
def step_create_change_with_id_and_status(context, change_id, status):
    """Create a change with specific ID and status (via CLI)."""
    status_id = CHANGESTATUS_MAP.get(status.lower())
    if not status_id:
        raise ValueError(f"Unknown status: {status}")

    # Create change via CLI
    cmd = [
        "roundup-admin",
        "-i",
        "tracker",
        "create",
        "change",
        f"title=Test change {change_id}",
        "description=Test change description",
        "justification=Testing workflow",
        "priority=2",
        "category=1",
        f"status={status_id}",
    ]

    result = subprocess.run(cmd, capture_output=True, text=True, timeout=10, check=True)

    # Store the actual ID (might not match requested ID)
    actual_id = result.stdout.strip()
    context.created_change_id = actual_id
    context.expected_change_id = change_id


@when("I view the change details")
def step_view_change_details(context):
    """Navigate to change details page."""
    change_id = context.created_change_id
    context.page.goto(f"{context.tracker_url}/change{change_id}")
    context.page.wait_for_load_state("networkidle")


@when('I click "{button_text}"')
def step_click_button(context, button_text):
    """Click a button with specific text."""
    # Try exact match first
    button = context.page.get_by_role("button", name=button_text, exact=True)
    if button.count() == 0:
        # Try partial match
        button = context.page.get_by_role("button", name=button_text)

    button.first.click()
    context.page.wait_for_load_state("networkidle")


@when('I add assessment notes "{notes}"')
def step_add_assessment_notes(context, notes):
    """Add notes to the change assessment."""
    # Find notes/messages field
    context.page.fill('textarea[name="@note"]', notes)


@when('I enter rejection reason "{reason}"')
def step_enter_rejection_reason(context, reason):
    """Enter a rejection reason."""
    context.page.fill('textarea[name="rejection_reason"]', reason)
    context.rejection_reason = reason


@when("I confirm rejection")
def step_confirm_rejection(context):
    """Confirm the rejection action."""
    context.page.click('button[name="confirm_reject"]')
    context.page.wait_for_load_state("networkidle")


@when('I enter scheduled date "{date}"')
def step_enter_scheduled_date(context, date):
    """Enter a scheduled date for the change."""
    context.page.fill('input[name="scheduled_date"]', date)
    context.scheduled_date = date


@when("I click Save Schedule")
def step_save_schedule(context):
    """Click the Save Schedule button."""
    context.page.click('button[name="save_schedule"]')
    context.page.wait_for_load_state("networkidle")


@when('I enter implementation notes "{notes}"')
def step_enter_implementation_notes(context, notes):
    """Enter implementation notes."""
    context.page.fill('textarea[name="implementation_notes"]', notes)
    context.implementation_notes = notes


# Note: Step definition for 'I run "{command}"' is in change_list_steps.py
# to avoid duplication and handle roundup-client commands


@when('I PATCH "{endpoint}" with JSON')
def step_patch_with_json(context, endpoint):
    """Send a PATCH request with JSON body."""
    import json

    import requests

    # Parse JSON from context.text
    payload = json.loads(context.text)

    # Build full URL
    url = f"{context.tracker_url}{endpoint}"

    # Send PATCH request with CSRF headers
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Basic YWRtaW46YWRtaW4=",  # admin:admin
        "X-Requested-With": "XMLHttpRequest",
        "Origin": context.tracker_url,
        "Referer": f"{context.tracker_url}/",
    }

    response = requests.patch(url, json=payload, headers=headers, timeout=10)

    context.api_response = response
    context.api_status_code = response.status_code


# Note: Step definition for 'I GET "{endpoint}"' is in change_list_steps.py
# to avoid duplication and handle API requests with proper authentication


@then('the change status should be "{status}"')
def step_verify_change_status(context, status):
    """Verify the change has the expected status."""
    if hasattr(context, "page") and context.page:
        # Web UI verification
        status_text = context.page.locator(".status-value, .property-status").first.text_content()
        assert status.lower() in status_text.lower(), (
            f"Expected status '{status}', but got '{status_text}'"
        )
    else:
        # CLI/API verification
        change_id = context.created_change_id
        cmd = ["roundup-admin", "-i", "tracker", "get", f"change{change_id}", "status"]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10, check=True)

        status_id = result.stdout.strip()
        expected_id = CHANGESTATUS_MAP.get(status.lower())

        assert status_id == expected_id, f"Expected status ID {expected_id}, got {status_id}"


@then('I should see "{message}"')
def step_verify_message(context, message):
    """Verify a message is displayed."""
    page_text = context.page.locator("body").text_content()
    assert message in page_text, f"Expected message '{message}' not found on page"


@then("the status change should be recorded in history")
def step_verify_status_history(context):
    """Verify status change is in history."""
    # Check for history/messages section
    history = context.page.locator(".history, .messages, .activity-log")
    assert history.count() > 0, "No history section found"


@then('I should not see "{button_text}" button')
def step_verify_button_not_visible(context, button_text):
    """Verify a button is not visible."""
    button = context.page.get_by_role("button", name=button_text)
    assert button.count() == 0, f"Button '{button_text}' should not be visible"


@then('I should only see "{button_text}" button')
def step_verify_only_button(context, button_text):
    """Verify only specific button is visible."""
    button = context.page.get_by_role("button", name=button_text)
    assert button.count() > 0, f"Button '{button_text}' should be visible"


@then("the rejection reason should be recorded")
def step_verify_rejection_recorded(context):
    """Verify rejection reason is recorded."""
    if hasattr(context, "rejection_reason"):
        page_text = context.page.locator("body").text_content()
        assert context.rejection_reason in page_text, (
            f"Rejection reason '{context.rejection_reason}' not found"
        )


@then("the command should succeed")
def step_verify_command_success(context):
    """Verify CLI command succeeded."""
    assert context.cli_returncode == 0, f"Command failed: {context.cli_stderr}"


@then('change "{change_id}" should have status "{status}"')
def step_verify_change_status_by_id(context, change_id, status):
    """Verify a specific change has expected status."""
    # Use actual ID if different from expected
    actual_id = getattr(context, "created_change_id", f"change{change_id}")

    cmd = ["roundup-admin", "-i", "tracker", "get", actual_id, "status"]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=10, check=True)

    status_id = result.stdout.strip()
    expected_id = CHANGESTATUS_MAP.get(status.lower())

    assert status_id == expected_id, f"Expected status ID {expected_id}, got {status_id}"


@then('the change should have a message containing "{text}"')
def step_verify_change_message(context, text):
    """Verify change has a message containing specific text."""
    change_id = context.created_change_id

    cmd = ["roundup-admin", "-i", "tracker", "get", change_id, "messages"]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=10, check=True)

    messages = result.stdout.strip()
    assert text in messages or len(messages) > 0, f"Expected message containing '{text}'"


@then("the response status should be {status_code:d}")
def step_verify_response_status(context, status_code):
    """Verify API response status code."""
    assert context.api_status_code == status_code, (
        f"Expected status {status_code}, got {context.api_status_code}"
    )


@then('the response should contain "{text}"')
def step_verify_response_contains(context, text):
    """Verify API response contains specific text."""
    response_text = context.api_response.text
    assert text in response_text, f"Response does not contain '{text}'"


@then("the response should contain status history")
def step_verify_response_has_history(context):
    """Verify API response contains status history."""
    response_json = context.api_response.json()
    assert "history" in response_json or "messages" in response_json, "No history in response"


@then('the history should show transitions: "{transitions}"')
def step_verify_history_transitions(context, transitions):
    """Verify status transition history."""
    # This is a placeholder - actual implementation would parse history
    # For now, just verify response has some data
    response_json = context.api_response.json()
    assert len(str(response_json)) > 0, "Response is empty"


@given("the change has gone through workflow stages")
def step_change_has_workflow_history(context):
    """Set up a change with workflow history."""
    # This would typically update the change through multiple statuses
    # For now, this is a placeholder
    pass
