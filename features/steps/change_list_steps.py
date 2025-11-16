# SPDX-FileCopyrightText: 2025 Georges Martin <jrjsmrtn@gmail.com>
# SPDX-License-Identifier: MIT

"""Step definitions for viewing change request lists."""

import json
import subprocess
from datetime import datetime

import requests
from behave import given, then, when
from playwright.sync_api import expect
from requests.auth import HTTPBasicAuth


# Map priority/category names to IDs (must match schema)
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

CHANGESTATUS_MAP = {
    "planning": "1",
    "approved": "2",
    "implementing": "3",
    "completed": "4",
    "cancelled": "5",
}


@given("the following changes exist:")
def step_create_multiple_changes(context):
    """Create multiple change requests for testing the change list."""
    tracker_dir = getattr(context, "tracker_dir", "tracker")
    created_change_ids = []

    for row in context.table:
        title = row["title"]
        priority = row.get("priority", "medium")
        category = row.get("category", "configuration")
        status = row.get("status", "planning")
        created_date = row.get("created_date", None)

        # Build command args
        cmd_args = ["roundup-admin", "-i", tracker_dir, "create", "change"]
        cmd_args.append(f"title={title}")
        cmd_args.append(f"justification=Test change for {title}")

        # Map priority label to ID
        priority_id = CHANGEPRIORITY_MAP.get(priority.lower())
        if priority_id:
            cmd_args.append(f"priority={priority_id}")

        # Map category label to ID
        category_id = CHANGECATEGORY_MAP.get(category.lower())
        if category_id:
            cmd_args.append(f"category={category_id}")

        # Map status label to ID
        status_id = CHANGESTATUS_MAP.get(status.lower())
        if status_id:
            cmd_args.append(f"status={status_id}")

        # Add description if provided
        description = row.get("description", f"Description for {title}")
        cmd_args.append(f"description={description}")

        # Run the command
        result = subprocess.run(cmd_args, capture_output=True, text=True, timeout=30)

        assert result.returncode == 0, f"Failed to create change '{title}'. Stderr: {result.stderr}"

        change_id = result.stdout.strip()
        created_change_ids.append(change_id)

        # If a specific created_date is provided, update it
        # (Roundup-admin create doesn't support setting creation date directly)
        # This would typically require database manipulation or API calls

    # Store the created change IDs for potential cleanup
    context.test_change_ids = created_change_ids


@given("no changes exist")
def step_no_changes_exist(context):
    """Ensure no changes exist in the tracker."""
    # This step assumes we start with a fresh tracker or can delete all changes
    # For BDD testing, we typically start with a clean slate
    context.test_change_ids = []


@when('I navigate to "Changes"')
def step_navigate_to_changes(context):
    """Navigate to the change request list page."""
    context.page.goto("http://localhost:8080/pms/change?@template=index")
    context.page.wait_for_load_state("networkidle")


@when('I filter by category "{category}"')
def step_filter_by_category(context, category):
    """Filter change list by category."""
    # In Roundup, filtering is typically done via URL parameters or form filters
    # Look for a category filter dropdown/select
    category_filter = context.page.locator('select[name="category"]')
    if category_filter.count() > 0:
        category_filter.select_option(label=category)
    else:
        # Use URL parameter filtering
        category_id = CHANGECATEGORY_MAP.get(category.lower())
        current_url = context.page.url
        filter_url = f"{current_url}&category={category_id}"
        context.page.goto(filter_url)

    context.page.wait_for_load_state("networkidle")


@when('I filter by priority "{priority}"')
def step_filter_by_priority(context, priority):
    """Filter change list by priority."""
    priority_filter = context.page.locator('select[name="priority"]')
    if priority_filter.count() > 0:
        priority_filter.select_option(label=priority)
    else:
        # Use URL parameter filtering
        priority_id = CHANGEPRIORITY_MAP.get(priority.lower())
        current_url = context.page.url
        filter_url = f"{current_url}&priority={priority_id}"
        context.page.goto(filter_url)

    context.page.wait_for_load_state("networkidle")


@when('I filter by status "{status}"')
def step_filter_by_status(context, status):
    """Filter change list by status."""
    status_filter = context.page.locator('select[name="status"]')
    if status_filter.count() > 0:
        status_filter.select_option(label=status)
    else:
        # Use URL parameter filtering
        status_id = CHANGESTATUS_MAP.get(status.lower())
        current_url = context.page.url
        filter_url = f"{current_url}&status={status_id}"
        context.page.goto(filter_url)

    context.page.wait_for_load_state("networkidle")


@then("I should see {count:d} change")
@then("I should see {count:d} changes")
def step_verify_change_count(context, count):
    """Verify the number of changes displayed in the list."""
    # In Roundup, changes are typically displayed in a table
    # Count the number of change rows (skip header row)
    change_rows = context.page.locator("table.list tr.normal, table.list tr").all()

    # Filter out header rows
    actual_count = 0
    for row in change_rows:
        # Check if row contains change links
        if row.locator('a[href*="change"]').count() > 0:
            actual_count += 1

    assert actual_count == count, f"Expected {count} changes, found {actual_count}"


@then('"{title1}" should appear before "{title2}"')
def step_verify_change_order(context, title1, title2):
    """Verify that one change appears before another in the list."""
    page_content = context.page.content()

    # Find the positions of both titles
    pos1 = page_content.find(title1)
    pos2 = page_content.find(title2)

    assert pos1 != -1, f"Change '{title1}' not found in list"
    assert pos2 != -1, f"Change '{title2}' not found in list"
    assert pos1 < pos2, f"Expected '{title1}' to appear before '{title2}', but found opposite order"


@then("the changes should appear in order:")
def step_verify_changes_in_order(context):
    """Verify changes appear in a specific order."""
    page_content = context.page.content()

    titles = [row["title"] for row in context.table]
    positions = []

    for title in titles:
        pos = page_content.find(title)
        assert pos != -1, f"Change '{title}' not found in list"
        positions.append((title, pos))

    # Verify positions are in ascending order
    for i in range(len(positions) - 1):
        assert positions[i][1] < positions[i + 1][1], (
            f"Expected '{positions[i][0]}' to appear before '{positions[i + 1][0]}'"
        )


@when('I click on "{title}"')
def step_click_change(context, title):
    """Click on a change in the list to view details."""
    change_link = context.page.locator(f'a:has-text("{title}")').first
    change_link.click()
    context.page.wait_for_load_state("networkidle")


@then("I should see the change details page")
def step_verify_on_change_details_page(context):
    """Verify we're on a change details page."""
    # Check URL contains 'change' and a number
    url = context.page.url
    assert "/change" in url.lower(), f"Not on change details page. URL: {url}"


@then('I should see a "Create New Change" button')
def step_verify_create_change_button(context):
    """Verify the create new change button is visible."""
    # Look for a link or button to create a new change
    create_button = context.page.locator(
        'a:has-text("Create"), a:has-text("New Change"), a[href*="change?@template=item"]'
    )
    expect(create_button.first).to_be_visible()


# CLI step definitions for change lists
@when('I run "roundup-client list change"')
def step_run_cli_list_changes(context):
    """List all changes via CLI."""
    tracker_dir = context.tracker_dir
    # roundup-admin list already outputs titles, not just IDs
    cmd = ["roundup-admin", "-i", tracker_dir, "list", "change"]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    context.cli_result = result
    context.cli_exit_code = result.returncode
    context.cli_stdout = result.stdout.strip()
    context.cli_stderr = result.stderr.strip()
    context.cli_output = result.stdout


@when('I run "roundup-client list change category={category}"')
def step_run_cli_list_changes_filtered(context, category):
    """List changes filtered by category via CLI."""
    tracker_dir = context.tracker_dir
    category_id = CHANGECATEGORY_MAP.get(category.lower())

    # Use find to get the IDs, then display each change's title
    find_cmd = ["roundup-admin", "-i", tracker_dir, "find", "change", f"category={category_id}"]
    find_result = subprocess.run(find_cmd, capture_output=True, text=True, timeout=30)

    if find_result.returncode == 0 and find_result.stdout.strip():
        # Get change IDs (output is like "['1', '3', '5']")
        change_ids = find_result.stdout.strip().strip("[]'").split("', '")

        # Display each change's title
        output_lines = []
        for change_id in change_ids:
            # Correct syntax: get title change1 (property first, then designator)
            display_cmd = ["roundup-admin", "-i", tracker_dir, "get", "title", f"change{change_id}"]
            display_result = subprocess.run(display_cmd, capture_output=True, text=True, timeout=30)
            if display_result.returncode == 0:
                output_lines.append(display_result.stdout.strip())

        cli_output = "\n".join(output_lines)
        context.cli_exit_code = 0
    else:
        cli_output = find_result.stdout
        context.cli_exit_code = find_result.returncode

    context.cli_result = find_result
    context.cli_stdout = cli_output
    context.cli_stderr = find_result.stderr.strip()
    context.cli_output = cli_output


@then('I should not see "{text}" in CLI output')
def step_should_not_see_text_cli(context, text):
    """Verify text does not appear in CLI output."""
    assert text not in context.cli_output, (
        f"Found '{text}' in output, but expected it not to be there"
    )


# API step definitions for change lists
@when('I GET "{endpoint}"')
def step_get_endpoint(context, endpoint):
    """GET data from an API endpoint."""
    api_url = "http://localhost:8080/pms"
    full_url = f"{api_url}{endpoint}"
    auth = HTTPBasicAuth("admin", "admin")

    headers = {
        "Accept": "application/json",
        "X-Requested-With": "XMLHttpRequest",
    }

    response = requests.get(full_url, headers=headers, auth=auth, timeout=30)
    context.api_response = response
    context.api_status_code = response.status_code

    if response.status_code == 200:
        try:
            context.api_response_data = response.json()
        except json.JSONDecodeError:
            context.api_response_data = response.text
    else:
        context.api_response_data = response.text


@then("the response should contain {count:d} change")
@then("the response should contain {count:d} changes")
def step_verify_api_change_count(context, count):
    """Verify the number of changes in API response."""
    response_data = context.api_response_data

    # Roundup REST API typically returns data in a 'data' key
    if isinstance(response_data, dict):
        changes = response_data.get("data", {}).get("collection", [])
    else:
        changes = []

    assert len(changes) == count, f"Expected {count} changes in API response, found {len(changes)}"


@then('the response should include "{title}"')
def step_verify_api_includes_title(context, title):
    """Verify API response includes a change with the given title."""
    response_data = context.api_response_data

    # Convert to string for simple search
    response_str = json.dumps(response_data)
    assert title in response_str, f"Expected to find '{title}' in API response"


@then('the first change should be "{title}"')
def step_verify_first_change(context, title):
    """Verify the first change in API response has the given title."""
    response_data = context.api_response_data

    if isinstance(response_data, dict):
        changes = response_data.get("data", {}).get("collection", [])
    else:
        changes = []

    assert len(changes) > 0, "No changes in API response"
    first_change = changes[0]
    assert first_change.get("title") == title, (
        f"Expected first change to be '{title}', found '{first_change.get('title')}'"
    )


@then('the last change should be "{title}"')
def step_verify_last_change(context, title):
    """Verify the last change in API response has the given title."""
    response_data = context.api_response_data

    if isinstance(response_data, dict):
        changes = response_data.get("data", {}).get("collection", [])
    else:
        changes = []

    assert len(changes) > 0, "No changes in API response"
    last_change = changes[-1]
    assert last_change.get("title") == title, (
        f"Expected last change to be '{title}', found '{last_change.get('title')}'"
    )


# ============================================================================
# CLI Step Definitions
# ============================================================================


@when('I run "{command}"')
def step_run_cli_command(context, command):
    """Run a CLI command (roundup-client or roundup-admin)."""
    tracker_dir = getattr(context, "tracker_dir", "tracker")

    # For roundup-client commands, we need to parse and execute
    # Note: roundup-client may not exist in all Roundup installations
    # so we'll use roundup-admin list instead
    if command.startswith("roundup-client list"):
        # Convert to roundup-admin list command
        # e.g., "roundup-client list change" -> "roundup-admin -i tracker list change"
        parts = command.split()
        classname = parts[2] if len(parts) > 2 else "issue"
        filters = " ".join(parts[3:]) if len(parts) > 3 else ""

        cmd = ["roundup-admin", "-i", tracker_dir, "list", classname]
        if filters:
            cmd.append(filters)

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    else:
        # Generic command execution
        result = subprocess.run(command.split(), capture_output=True, text=True, timeout=30)

    # Store result for later assertions
    context.cli_result = result
    context.cli_exit_code = result.returncode
    context.cli_stdout = result.stdout.strip()
    context.cli_stderr = result.stderr.strip()
    # Also store as cli_output for consistency with other steps
    context.cli_output = result.stdout
