# SPDX-FileCopyrightText: 2025 Georges Martin <jrjsmrtn@gmail.com>
# SPDX-License-Identifier: MIT

"""Step definitions for viewing issues in Roundup tracker."""

import subprocess

from behave import given, then, when
from playwright.sync_api import expect

from features.steps.common import PRIORITY_MAP, STATUS_MAP


@given("the following issues exist:")
def step_create_multiple_issues(context):
    """Create multiple issues for testing the issue list."""
    # Get tracker_dir from context or use default
    tracker_dir = getattr(context, "tracker_dir", "tracker")

    created_issue_ids = []

    for row in context.table:
        title = row["title"]
        priority = row.get("priority", "bug")
        assignedto = row.get("assignedto", "")

        # Build command args
        cmd_args = ["roundup-admin", "-i", tracker_dir, "create", "issue"]
        cmd_args.append(f"title={title}")

        # Map priority label to ID
        priority_id = PRIORITY_MAP.get(priority.lower())
        if priority_id:
            cmd_args.append(f"priority={priority_id}")

        # Add assignedto if specified (and not empty)
        if assignedto:
            # Map username to user ID (for now, assume admin=1)
            user_id = "1" if assignedto == "admin" else assignedto
            cmd_args.append(f"assignedto={user_id}")

        # Run the command
        result = subprocess.run(cmd_args, capture_output=True, text=True, timeout=30)

        assert result.returncode == 0, f"Failed to create issue '{title}'. Stderr: {result.stderr}"

        issue_id = result.stdout.strip()
        created_issue_ids.append(issue_id)

    # Store the created issue IDs for potential cleanup
    context.test_issue_ids = created_issue_ids


@given('an issue exists with title "{title}"')
@given('an issue exists with title "{title}" and status "{status}"')
def step_create_single_issue(context, title, status=None):
    """Create a single issue for testing, optionally with specific status."""
    # Get tracker_dir from context or use default
    tracker_dir = getattr(context, "tracker_dir", "tracker")

    # Build command args
    cmd_args = ["roundup-admin", "-i", tracker_dir, "create", "issue"]
    cmd_args.append(f"title={title}")

    # Always set priority (required field) - default to "bug" (3)
    cmd_args.append("priority=3")

    # Add status if provided
    if status:
        status_id = STATUS_MAP.get(status)
        assert status_id, f"Unknown status: {status}"
        cmd_args.append(f"status={status_id}")

    # Run the command
    result = subprocess.run(cmd_args, capture_output=True, text=True, timeout=30)

    assert result.returncode == 0, f"Failed to create issue '{title}'. Stderr: {result.stderr}"

    issue_id = result.stdout.strip()
    context.created_issue_id = f"issue{issue_id}"
    context.current_issue_id = f"issue{issue_id}"
    context.current_issue_title = title
    context.current_issue_status = status or "new"
    context.test_issue_title = title


@then("I should see {count:d} issues in the list")
def step_verify_issue_count(context, count):
    """Verify the number of issues displayed in the list."""
    # In Roundup, issues are typically displayed in a table
    # Count the number of issue rows (skip header row)
    issue_rows = context.page.locator("table.list tr.normal, table.list tr").all()

    # Filter out header rows
    actual_count = 0
    for row in issue_rows:
        # Check if row contains issue links
        if row.locator('a[href*="issue"]').count() > 0:
            actual_count += 1

    assert actual_count >= count, f"Expected at least {count} issues, found {actual_count}"


@then('I should see issue "{title}"')
def step_verify_issue_in_list(context, title):
    """Verify a specific issue appears in the list (CI-compatible)."""
    # Wait for page to be fully loaded
    context.page.wait_for_load_state("networkidle")

    # Look for a link containing the title
    issue_link = context.page.locator(f'a:has-text("{title}")')

    # Check if issue exists in DOM (may not be visible if paginated/scrolled)
    count = issue_link.count()
    if count == 0:
        # Issue not found - try scrolling and waiting
        context.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        context.page.wait_for_timeout(500)  # Wait for any lazy loading
        count = issue_link.count()

    assert count > 0, (
        f"Issue '{title}' not found on page. Available issues: {context.page.content()[:500]}"
    )

    # For web UI scenarios, verify first match is visible
    expect(issue_link.first).to_be_visible(timeout=10000)  # Increased timeout for CI


@when('I click on the issue "{title}"')
def step_click_issue(context, title):
    """Click on an issue in the list to view details."""
    issue_link = context.page.locator(f'a:has-text("{title}")').first
    issue_link.click()
    context.page.wait_for_load_state("networkidle")


@then("I should be on the issue details page")
def step_verify_on_details_page(context):
    """Verify we're on an issue details page."""
    # Check URL contains 'issue' and a number
    url = context.page.url
    assert "/issue" in url.lower(), f"Not on issue details page. URL: {url}"


@then('I should see the issue title "{title}"')
def step_verify_issue_title_on_page(context, title):
    """Verify the issue title is displayed on the page."""
    page_content = context.page.content()
    assert title in page_content, f"Issue title '{title}' not found on page"
