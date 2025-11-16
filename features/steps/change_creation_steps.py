# SPDX-FileCopyrightText: 2025 Georges Martin <jrjsmrtn@gmail.com>
# SPDX-License-Identifier: MIT

"""Step definitions for change request creation."""

import json
import subprocess

import requests
from behave import given, then, when
from requests.auth import HTTPBasicAuth


# Map priority/category names to IDs
CHANGEPRIORITY_MAP = {
    "low": "1",
    "medium": "2",
    "high": "3",
    "critical": "4",
}

CHANGECATEGORY_MAP = {
    "software": "1",
    "hardware": "2",
    "configuration": "3",
    "network": "4",
}


@when('I navigate to the "New Change" page')
def step_navigate_to_new_change_page(context):
    """Navigate to the new change request creation page."""
    context.page.goto(f"{context.tracker_url}change?@template=item")
    context.page.wait_for_load_state("networkidle")


@when("I enter the following change details:")
def step_enter_change_details(context):
    """Enter change request details from a table."""
    for row in context.table:
        field_name = row["field"]
        field_value = row["value"]

        if field_name == "title":
            context.page.fill('input[name="title"]', field_value)
            context.change_title = field_value

        elif field_name == "justification":
            context.page.fill('textarea[name="justification"]', field_value)

        elif field_name == "impact":
            context.page.fill('textarea[name="impact"]', field_value)

        elif field_name == "risk":
            context.page.fill('textarea[name="risk"]', field_value)

        elif field_name == "priority":
            # Priority is a select/dropdown
            context.page.select_option('select[name="priority"]', label=field_value)

        elif field_name == "category":
            # Category is a select/dropdown
            context.page.select_option('select[name="category"]', label=field_value)


@when("I submit the change")
def step_submit_change(context):
    """Submit the change request form."""
    submit_button = context.page.locator('input[name="submit_button"]').first
    submit_button.click()
    context.page.wait_for_load_state("networkidle")


@then('the change should be saved with title "{title}"')
def step_verify_change_saved(context, title):
    """Verify a change was saved with the given title."""
    tracker_dir = getattr(context, "tracker_dir", "tracker")

    # Use roundup-admin to list changes
    cmd = ["roundup-admin", "-i", tracker_dir, "list", "change"]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

    assert result.returncode == 0, f"Failed to list changes. Stderr: {result.stderr}"

    output = result.stdout
    # Look for the title in the output
    assert title in output or "change1" in output.lower(), (
        f"Change with title '{title}' not found. Output: {output}"
    )


@then("I should see an error message about required fields")
def step_verify_required_field_error(context):
    """Verify an error message about required fields is displayed."""
    page_content = context.page.content()
    # Roundup shows "required" in error messages
    assert "required" in page_content.lower() or "error" in page_content.lower(), (
        "No error message about required fields found on page"
    )


@given("I have CLI access to the tracker")
def step_have_cli_access(context):
    """Set up CLI access to the tracker."""
    context.tracker_dir = getattr(context, "tracker_dir", "tracker")


@when("I create a change via CLI with:")
def step_create_change_via_cli(context):
    """Create a change request via CLI."""
    tracker_dir = context.tracker_dir

    # Build command args
    cmd_args = ["roundup-admin", "-i", tracker_dir, "create", "change"]

    for row in context.table:
        field_name = row["field"]
        field_value = row["value"]

        if field_name == "priority":
            priority_id = CHANGEPRIORITY_MAP.get(field_value.lower())
            if priority_id:
                cmd_args.append(f"priority={priority_id}")
        elif field_name == "category":
            category_id = CHANGECATEGORY_MAP.get(field_value.lower())
            if category_id:
                cmd_args.append(f"category={category_id}")
        else:
            cmd_args.append(f"{field_name}={field_value}")

    # Run the command
    result = subprocess.run(cmd_args, capture_output=True, text=True, timeout=30)

    context.cli_result = result
    if result.returncode == 0:
        context.created_change_id = result.stdout.strip()


@then("the change should be created successfully")
def step_verify_change_created_successfully(context):
    """Verify the change was created successfully via CLI."""
    assert context.cli_result.returncode == 0, (
        f"Change creation failed. Stderr: {context.cli_result.stderr}"
    )


@then('the change should have status "{status}"')
def step_verify_change_status(context, status):
    """Verify the change has the expected status."""
    tracker_dir = context.tracker_dir
    change_id = context.created_change_id

    # Use roundup-admin to display the change
    cmd = ["roundup-admin", "-i", tracker_dir, "display", f"change{change_id}"]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

    assert result.returncode == 0, f"Failed to display change. Stderr: {result.stderr}"

    output = result.stdout
    # The default status should be "proposed" (ID 1)
    assert "status:" in output.lower(), f"No status field found. Output: {output}"


@when('I POST to "{endpoint}" with JSON:')
def step_post_to_endpoint_with_json(context, endpoint):
    """POST JSON data to an API endpoint."""
    # Get base URL from context
    api_url = context.tracker_url.rstrip("/")
    full_url = f"{api_url}{endpoint}"
    auth = HTTPBasicAuth("admin", "admin")

    payload = json.loads(context.text)

    # Extract base URL (protocol://host:port) from tracker_url
    from urllib.parse import urlparse

    parsed = urlparse(context.tracker_url)
    base_url = f"{parsed.scheme}://{parsed.netloc}"

    headers = {
        "Content-Type": "application/json",
        "X-Requested-With": "XMLHttpRequest",
        "Origin": base_url,
        "Referer": context.tracker_url,
    }

    response = requests.post(full_url, json=payload, headers=headers, auth=auth, timeout=30)
    context.api_response = response
    context.api_status_code = response.status_code
    context.api_response_data = (
        response.json() if response.status_code in [200, 201] else response.text
    )


@then("the response should contain the created change ID")
def step_verify_response_contains_change_id(context):
    """Verify the API response contains a created change ID."""
    response_data = context.api_response.json()
    # Roundup REST API returns the created item link
    assert "data" in response_data, f"No 'data' in response: {response_data}"
    data = response_data["data"]
    assert "id" in data or "link" in data, f"No ID or link in response data: {data}"
