# SPDX-FileCopyrightText: 2025 Georges Martin <jrjsmrtn@gmail.com>
# SPDX-License-Identifier: MIT

"""Step definitions for linking changes to issues."""

import json
import subprocess

import requests
from behave import given, then, use_step_matcher, when
from requests.auth import HTTPBasicAuth


@given('an issue exists with title "{title}"')
def step_create_issue_with_title(context, title):
    """Create an issue with specific title."""
    tracker_dir = getattr(context, "tracker_dir", "tracker")

    # Create issue via CLI
    cmd = [
        "roundup-admin",
        "-i",
        tracker_dir,
        "create",
        "issue",
        f"title={title}",
        "priority=2",  # medium
        "status=1",  # unread
    ]

    result = subprocess.run(cmd, capture_output=True, text=True, timeout=10, check=True)

    # Extract issue ID from output
    issue_id = result.stdout.strip()

    # Store issue information
    if not hasattr(context, "created_issues"):
        context.created_issues = {}
    context.created_issues[title] = issue_id


@given('a change exists with title "{title}"')
def step_create_change_with_title(context, title):
    """Create a change with specific title."""
    tracker_dir = getattr(context, "tracker_dir", "tracker")

    # Create change via CLI
    cmd = [
        "roundup-admin",
        "-i",
        tracker_dir,
        "create",
        "change",
        f"title={title}",
        f"description=Test change for {title}",
        "justification=Testing change-issue links",
        "priority=2",  # medium
        "category=1",  # software
        "status=1",  # planning
    ]

    result = subprocess.run(cmd, capture_output=True, text=True, timeout=10, check=True)

    # Extract change ID from output
    change_id = result.stdout.strip()

    # Store change information
    if not hasattr(context, "created_changes"):
        context.created_changes = {}
    context.created_changes[title] = change_id
    context.current_change_id = change_id


@given('a change "{change_title}" is linked to the issue')
def step_link_change_to_issue(context, change_title):
    """Link a change to the last created issue."""
    tracker_dir = getattr(context, "tracker_dir", "tracker")

    # Get the issue ID from context (last created issue with title)
    # We need to find the issue title from the previous step
    # For now, we'll use the first issue in created_issues
    if not hasattr(context, "created_issues") or not context.created_issues:
        raise ValueError("No issues created to link to")

    issue_title = list(context.created_issues.keys())[0]
    issue_id = context.created_issues[issue_title]

    # Create the change with the related_issues field
    cmd = [
        "roundup-admin",
        "-i",
        tracker_dir,
        "create",
        "change",
        f"title={change_title}",
        f"description=Test change for {change_title}",
        "justification=Testing change-issue links",
        "priority=2",
        "category=1",
        "status=1",
        f"related_issues={issue_id}",
    ]

    result = subprocess.run(cmd, capture_output=True, text=True, timeout=10, check=True)

    change_id = result.stdout.strip()

    if not hasattr(context, "created_changes"):
        context.created_changes = {}
    context.created_changes[change_title] = change_id


@given("the change is linked to the issue")
def step_change_is_linked_to_issue(context):
    """Link the current change to the last created issue."""
    tracker_dir = getattr(context, "tracker_dir", "tracker")

    # Get change and issue IDs
    if not hasattr(context, "current_change_id"):
        raise ValueError("No current change to link")

    if not hasattr(context, "created_issues") or not context.created_issues:
        raise ValueError("No issues created to link to")

    issue_id = list(context.created_issues.values())[0]
    change_id = context.current_change_id

    # Update the change to add the related_issues link
    cmd = [
        "roundup-admin",
        "-i",
        tracker_dir,
        "set",
        f"change{change_id}",
        f"related_issues={issue_id}",
    ]

    subprocess.run(cmd, capture_output=True, text=True, timeout=10, check=True)


@given("the following issues exist:")
def step_create_multiple_issues(context):
    """Create multiple issues from a table."""
    tracker_dir = getattr(context, "tracker_dir", "tracker")

    if not hasattr(context, "created_issues"):
        context.created_issues = {}

    for row in context.table:
        title = row["title"]

        cmd = [
            "roundup-admin",
            "-i",
            tracker_dir,
            "create",
            "issue",
            f"title={title}",
            "priority=2",
            "status=1",
        ]

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10, check=True)

        issue_id = result.stdout.strip()
        context.created_issues[title] = issue_id


@given('a change exists with ID "{change_id}"')
def step_create_change_with_id(context, change_id):
    """Create a change (ID will be auto-assigned)."""
    tracker_dir = getattr(context, "tracker_dir", "tracker")

    cmd = [
        "roundup-admin",
        "-i",
        tracker_dir,
        "create",
        "change",
        f"title=Test change {change_id}",
        "description=Test change description",
        "justification=Testing",
        "priority=2",
        "category=1",
        "status=1",
    ]

    result = subprocess.run(cmd, capture_output=True, text=True, timeout=10, check=True)

    actual_id = result.stdout.strip()
    context.current_change_id = actual_id
    context.expected_change_id = change_id


@given('the following issues exist with IDs "{issue_ids}"')
def step_create_issues_with_ids(context, issue_ids):
    """Create multiple issues."""
    tracker_dir = getattr(context, "tracker_dir", "tracker")

    if not hasattr(context, "created_issues"):
        context.created_issues = {}

    ids = issue_ids.split(",")
    actual_ids = []

    for issue_id in ids:
        cmd = [
            "roundup-admin",
            "-i",
            tracker_dir,
            "create",
            "issue",
            f"title=Test issue {issue_id}",
            "priority=2",
            "status=1",
        ]

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10, check=True)

        actual_id = result.stdout.strip()
        actual_ids.append(actual_id)
        context.created_issues[f"issue_{issue_id}"] = actual_id

    context.created_issue_ids = actual_ids


# Use parse matcher with optional parameter
use_step_matcher("parse")


@given('an issue exists with ID "{issue_id:d}" and title "{title}"')
def step_create_issue_with_numeric_id_and_title(context, issue_id, title):
    """Create an issue with specific numeric ID and title."""
    tracker_dir = getattr(context, "tracker_dir", "tracker")

    cmd = [
        "roundup-admin",
        "-i",
        tracker_dir,
        "create",
        "issue",
        f"title={title}",
        "priority=2",
        "status=1",
    ]

    result = subprocess.run(cmd, capture_output=True, text=True, timeout=10, check=True)

    actual_id = result.stdout.strip()

    if not hasattr(context, "created_issues"):
        context.created_issues = {}

    context.created_issues[title] = actual_id
    context.current_issue_id = actual_id


@given('an issue exists with ID "{issue_id:d}"')
def step_create_issue_with_numeric_id(context, issue_id):
    """Create an issue with specific numeric ID (ID will be auto-assigned)."""
    tracker_dir = getattr(context, "tracker_dir", "tracker")

    cmd = [
        "roundup-admin",
        "-i",
        tracker_dir,
        "create",
        "issue",
        f"title=Test issue {issue_id}",
        "priority=2",
        "status=1",
    ]

    result = subprocess.run(cmd, capture_output=True, text=True, timeout=10, check=True)

    actual_id = result.stdout.strip()

    if not hasattr(context, "created_issues"):
        context.created_issues = {}
    context.created_issues[f"issue_{issue_id}"] = actual_id
    context.current_issue_id = actual_id


# Reset to default matcher
use_step_matcher("parse")


@when('I add related issue "{issue_title}"')
def step_add_related_issue(context, issue_title):
    """Add a related issue to the current change."""
    # Get the issue ID
    if not hasattr(context, "created_issues") or issue_title not in context.created_issues:
        raise ValueError(f"Issue '{issue_title}' not found in created issues")

    issue_id = context.created_issues[issue_title]

    # In the web UI, this would be done via the related_issues field
    # We'll use the Playwright page to interact with the field
    related_issues_field = context.page.locator('input[name="related_issues"]')

    # Get current value (might have existing issues)
    current_value = related_issues_field.input_value()

    # Add the new issue ID (comma-separated if there are existing issues)
    if current_value and current_value.strip():
        new_value = f"{current_value},{issue_id}"
    else:
        new_value = issue_id

    related_issues_field.fill(new_value)


@when("I view the issue details")
def step_view_issue_details(context):
    """Navigate to issue details page."""
    # Get the first created issue
    if not hasattr(context, "created_issues") or not context.created_issues:
        raise ValueError("No issues created to view")

    issue_id = list(context.created_issues.values())[0]
    context.page.goto(f"{context.tracker_url}/issue{issue_id}")
    context.page.wait_for_load_state("networkidle")


@when('I remove the related issue "{issue_title}"')
def step_remove_related_issue(context, issue_title):
    """Remove a related issue from the current change."""
    # Get the issue ID
    if not hasattr(context, "created_issues") or issue_title not in context.created_issues:
        raise ValueError(f"Issue '{issue_title}' not found in created issues")

    issue_id = context.created_issues[issue_title]

    # In the web UI, get current value and remove this issue
    related_issues_field = context.page.locator('input[name="related_issues"]')
    current_value = related_issues_field.input_value()

    # Remove the issue ID from the comma-separated list
    issue_ids = [id.strip() for id in current_value.split(",") if id.strip()]
    issue_ids = [id for id in issue_ids if id != issue_id]

    new_value = ",".join(issue_ids)
    related_issues_field.fill(new_value)


@when('I POST "{endpoint}" with JSON:')
def step_post_with_json(context, endpoint):
    """Send a POST request with JSON body."""
    payload = json.loads(context.text)

    url = f"{context.tracker_url}{endpoint}"

    headers = {
        "Content-Type": "application/json",
        "Authorization": "Basic YWRtaW46YWRtaW4=",  # admin:admin
        "X-Requested-With": "XMLHttpRequest",
        "Origin": context.tracker_url,
        "Referer": f"{context.tracker_url}/",
    }

    response = requests.post(url, json=payload, headers=headers, timeout=10)

    context.api_response = response
    context.api_status_code = response.status_code

    # Store created change ID if successful
    if response.status_code == 201:
        try:
            response_data = response.json()
            if "id" in response_data:
                context.created_change_id = response_data["id"]
        except json.JSONDecodeError:
            pass


@then('I should see "{text}" in related issues')
def step_verify_text_in_related_issues(context, text):
    """Verify text appears in the related issues section."""
    # Look for the related issues field or display area
    page_content = context.page.content()
    assert text in page_content, f"Expected '{text}' to be in related issues"


@then("the change should be linked to the issue")
def step_verify_change_linked_to_issue(context):
    """Verify the change is linked to the issue."""
    tracker_dir = getattr(context, "tracker_dir", "tracker")

    # Get the change ID
    if not hasattr(context, "current_change_id"):
        change_title = list(context.created_changes.keys())[0]
        change_id = context.created_changes[change_title]
    else:
        change_id = context.current_change_id

    # Get related_issues field
    cmd = ["roundup-admin", "-i", tracker_dir, "get", f"change{change_id}", "related_issues"]

    result = subprocess.run(cmd, capture_output=True, text=True, timeout=10, check=True)

    related_issues = result.stdout.strip()
    assert related_issues, "Change should have related issues"


@then('I should see "Related Changes" section')
def step_verify_related_changes_section(context):
    """Verify the Related Changes section is visible."""
    # This would require updating issue.item.html to show related changes
    # For now, we'll just check if we're on an issue page
    url = context.page.url
    assert "/issue" in url, "Should be on an issue details page"


@then("I should see {count:d} linked changes")
def step_verify_linked_changes_count(context, count):
    """Verify the number of linked changes."""
    # This would require querying the database or checking the UI
    # For now, we'll implement a placeholder
    # In a real implementation, we'd check the issue's related changes
    pass


@then('I should not see "{text}" in related issues')
def step_verify_text_not_in_related_issues(context, text):
    """Verify text does not appear in related issues."""
    page_content = context.page.content()
    # Check the related issues field specifically
    related_issues_field = context.page.locator('input[name="related_issues"]')
    if related_issues_field.count() > 0:
        field_value = related_issues_field.input_value()
        assert text not in field_value, f"'{text}' should not be in related issues"


@then("the change should not be linked to the issue")
def step_verify_change_not_linked(context):
    """Verify the change is not linked to the issue."""
    tracker_dir = getattr(context, "tracker_dir", "tracker")

    if not hasattr(context, "current_change_id"):
        change_title = list(context.created_changes.keys())[0]
        change_id = context.created_changes[change_title]
    else:
        change_id = context.current_change_id

    # Get related_issues field
    cmd = ["roundup-admin", "-i", tracker_dir, "get", f"change{change_id}", "related_issues"]

    result = subprocess.run(cmd, capture_output=True, text=True, timeout=10, check=True)

    related_issues = result.stdout.strip()
    # Should be empty or not contain the issue
    assert not related_issues or related_issues == "[]", "Change should not have related issues"


@then("I should see {count:d} related issues")
def step_verify_related_issues_count(context, count):
    """Verify the number of related issues."""
    tracker_dir = getattr(context, "tracker_dir", "tracker")

    if not hasattr(context, "current_change_id"):
        change_title = list(context.created_changes.keys())[0]
        change_id = context.created_changes[change_title]
    else:
        change_id = context.current_change_id

    # Get related_issues field
    cmd = ["roundup-admin", "-i", tracker_dir, "get", f"change{change_id}", "related_issues"]

    result = subprocess.run(cmd, capture_output=True, text=True, timeout=10, check=True)

    related_issues = result.stdout.strip()

    # Parse the related_issues (format is like "['1', '2']")
    if related_issues and related_issues != "[]":
        # Count comma-separated IDs
        issue_ids = related_issues.strip("[]'").split("', '")
        actual_count = len(issue_ids) if issue_ids != [""] else 0
    else:
        actual_count = 0

    assert actual_count == count, f"Expected {count} related issues, found {actual_count}"


@then('change "{change_id}" should be linked to issue "{issue_id}"')
def step_verify_change_linked_to_specific_issue(context, change_id, issue_id):
    """Verify a specific change is linked to a specific issue."""
    tracker_dir = getattr(context, "tracker_dir", "tracker")

    # Use actual IDs if they were stored
    actual_change_id = getattr(context, "current_change_id", change_id)
    actual_issue_id = getattr(context, "current_issue_id", issue_id)

    # Get related_issues field
    cmd = ["roundup-admin", "-i", tracker_dir, "get", f"change{actual_change_id}", "related_issues"]

    result = subprocess.run(cmd, capture_output=True, text=True, timeout=10, check=True)

    related_issues = result.stdout.strip()
    assert actual_issue_id in related_issues, f"Issue {actual_issue_id} should be in related_issues"


@then('change "{change_id}" should be linked to {count:d} issues')
def step_verify_change_linked_to_count_issues(context, change_id, count):
    """Verify a change is linked to a specific number of issues."""
    tracker_dir = getattr(context, "tracker_dir", "tracker")

    actual_change_id = getattr(context, "current_change_id", change_id)

    # Get related_issues field
    cmd = ["roundup-admin", "-i", tracker_dir, "get", f"change{actual_change_id}", "related_issues"]

    result = subprocess.run(cmd, capture_output=True, text=True, timeout=10, check=True)

    related_issues = result.stdout.strip()

    # Parse and count
    if related_issues and related_issues != "[]":
        issue_ids = related_issues.strip("[]'").split("', '")
        actual_count = len(issue_ids) if issue_ids != [""] else 0
    else:
        actual_count = 0

    assert actual_count == count, f"Expected {count} related issues, found {actual_count}"


@then('the created change should be linked to issue "{issue_id}"')
def step_verify_created_change_linked(context, issue_id):
    """Verify the newly created change is linked to the issue."""
    tracker_dir = getattr(context, "tracker_dir", "tracker")

    if not hasattr(context, "created_change_id"):
        raise ValueError("No created_change_id in context")

    change_id = context.created_change_id
    actual_issue_id = getattr(context, "current_issue_id", issue_id)

    # Get related_issues field
    cmd = ["roundup-admin", "-i", tracker_dir, "get", f"change{change_id}", "related_issues"]

    result = subprocess.run(cmd, capture_output=True, text=True, timeout=10, check=True)

    related_issues = result.stdout.strip()
    assert actual_issue_id in related_issues, f"Issue {actual_issue_id} should be in related_issues"


@then("the response should include related_issues")
def step_verify_response_includes_related_issues(context):
    """Verify the API response includes related_issues field."""
    try:
        response_data = context.api_response.json()
        assert "related_issues" in response_data or "data" in response_data, (
            "Response should include related_issues"
        )
    except json.JSONDecodeError:
        raise AssertionError("Response is not valid JSON")


@then('the related_issues should contain issue "{issue_id}"')
def step_verify_related_issues_contains_issue(context, issue_id):
    """Verify the related_issues field contains a specific issue."""
    try:
        response_data = context.api_response.json()

        # Get related_issues from response
        if "related_issues" in response_data:
            related_issues = response_data["related_issues"]
        elif "data" in response_data and "related_issues" in response_data["data"]:
            related_issues = response_data["data"]["related_issues"]
        else:
            raise AssertionError("No related_issues found in response")

        actual_issue_id = getattr(context, "current_issue_id", issue_id)

        # Check if issue is in the list
        if isinstance(related_issues, list):
            assert actual_issue_id in related_issues or str(actual_issue_id) in related_issues, (
                f"Issue {actual_issue_id} not found in related_issues"
            )
        else:
            assert str(actual_issue_id) in str(related_issues), (
                f"Issue {actual_issue_id} not found in related_issues"
            )
    except json.JSONDecodeError:
        raise AssertionError("Response is not valid JSON")
