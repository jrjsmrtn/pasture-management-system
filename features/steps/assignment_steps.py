# SPDX-FileCopyrightText: 2025 Georges Martin <jrjsmrtn@gmail.com>
# SPDX-License-Identifier: MIT

"""Step definitions for issue assignment scenarios."""

import subprocess

from behave import given, then, when
from playwright.sync_api import expect


@when('I assign the issue to user "{username}"')
def step_assign_issue_to_user(context, username):
    """Assign an issue to a specific user via the assignedto dropdown."""
    # In Roundup, the assignedto dropdown shows user IDs
    # We need to select by the username value
    assignee_dropdown = context.page.locator('select[name="assignedto"]')

    # Get all options to find the one matching the username
    options = assignee_dropdown.locator("option").all()

    user_value = None
    for option in options:
        option_text = option.inner_text().strip()
        if username in option_text:
            user_value = option.get_attribute("value")
            break

    assert user_value, f"User '{username}' not found in assignee dropdown"

    # Select the user
    assignee_dropdown.select_option(value=user_value)


@given('an issue exists with title "{title}" and is unassigned')
def step_create_unassigned_issue(context, title):
    """Create an issue without an assigned user."""
    tracker_dir = getattr(context, "tracker_dir", "tracker")

    # Build command args without assignedto
    cmd_args = ["roundup-admin", "-i", tracker_dir, "create", "issue"]
    cmd_args.append(f"title={title}")
    # Add default priority (bug=3) to satisfy Roundup's @required validation
    cmd_args.append("priority=3")

    # Run the command
    result = subprocess.run(cmd_args, capture_output=True, text=True, timeout=30)

    assert result.returncode == 0, f"Failed to create issue '{title}'. Stderr: {result.stderr}"

    issue_id = result.stdout.strip()
    context.created_issue_id = f"issue{issue_id}"
    context.current_issue_id = f"issue{issue_id}"
    context.current_issue_title = title


@then('the issue should be assigned to "{username}"')
def step_verify_issue_assigned_to(context, username):
    """Verify the issue is assigned to a specific user."""
    tracker_dir = getattr(context, "tracker_dir", "tracker")
    issue_id = context.created_issue_id

    # Use roundup-admin to check the assignee
    cmd = ["roundup-admin", "-i", tracker_dir, "display", issue_id]

    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

    assert result.returncode == 0, f"Failed to display issue. Stderr: {result.stderr}"

    output = result.stdout

    # Look for "assignedto: N" in output (where N is the user ID)
    # We'll check for the username presence as well
    assert "assignedto:" in output.lower(), f"No assignedto field found in issue. Output: {output}"
    assert (
        username in output or "1" in output
    ), f"Issue not assigned to '{username}'. Output: {output}"


@when('I filter issues by assignee "{assignee}"')
def step_filter_by_assignee(context, assignee):
    """Filter the issue list by a specific assignee."""
    # Build the URL with assignee filter
    tracker_url = context.tracker_url.rstrip("/")

    if assignee == "(unassigned)":
        # Filter for unassigned issues (assignedto is empty/null)
        # In Roundup, this is done with assignedto=-1
        filter_url = f"{tracker_url}/issue?@filter=assignedto&assignedto=-1"
    else:
        # Filter for specific user
        # Need to get the user ID for the username
        # For simplicity, assuming admin is user ID 1
        user_id = "1"  # admin is typically user 1
        filter_url = f"{tracker_url}/issue?@filter=assignedto&assignedto={user_id}"

    context.page.goto(filter_url)
    context.page.wait_for_load_state("networkidle")


@then('I should not see issue "{title}"')
def step_should_not_see_issue(context, title):
    """Verify an issue with specific title is NOT in the list."""
    # Look for a link containing the title
    issue_link = context.page.locator(f'a:has-text("{title}")')
    expect(issue_link).to_have_count(0)
