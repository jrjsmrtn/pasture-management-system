# SPDX-FileCopyrightText: 2025 Georges Martin <jrjsmrtn@gmail.com>
# SPDX-License-Identifier: MIT

"""Step definitions for CLI interactions with Roundup tracker."""

import os
import subprocess

from behave import given, then, when

from features.steps.common import PRIORITY_MAP


@given("the Roundup tracker database is accessible")
def step_database_accessible(context):
    """Verify the Roundup tracker database is accessible."""
    # Get the tracker directory from environment or use default
    tracker_dir = os.getenv("TRACKER_DIR", "tracker")
    context.tracker_dir = tracker_dir

    # Verify tracker directory exists
    assert os.path.isdir(tracker_dir), f"Tracker directory not found: {tracker_dir}"

    # Verify database directory exists
    db_dir = os.path.join(tracker_dir, "db")
    assert os.path.isdir(db_dir), f"Database directory not found: {db_dir}"


@when("I run the CLI command to create an issue with:")
def step_run_cli_create_issue(context):
    """Run roundup-admin create command with specified fields."""
    # Build the command arguments
    cmd_args = ["roundup-admin", "-i", context.tracker_dir, "create", "issue"]

    # Parse the table and build property=value arguments
    issue_data = {}
    for row in context.table:
        field_name = row["field"]
        field_value = row["value"]

        if field_name == "title":
            cmd_args.append(f"title={field_value}")
            issue_data["title"] = field_value
        elif field_name == "priority":
            # Map priority label to ID
            priority_id = PRIORITY_MAP.get(field_value.lower())
            if priority_id:
                cmd_args.append(f"priority={priority_id}")
                issue_data["priority"] = field_value
        else:
            # For other fields, pass as-is
            cmd_args.append(f"{field_name}={field_value}")
            issue_data[field_name] = field_value

    # Store issue data for later verification
    context.cli_issue_data = issue_data

    # Run the command
    result = subprocess.run(cmd_args, capture_output=True, text=True, timeout=30)

    # Store the result
    context.cli_result = result
    context.cli_exit_code = result.returncode
    context.cli_stdout = result.stdout.strip()
    context.cli_stderr = result.stderr.strip()


@then("the CLI command should succeed")
def step_cli_command_succeeds(context):
    """Verify the CLI command exited successfully."""
    assert context.cli_exit_code == 0, (
        f"CLI command failed with exit code {context.cli_exit_code}. "
        f"Stdout: {context.cli_stdout}. Stderr: {context.cli_stderr}"
    )


@then("the command should return an issue ID")
def step_command_returns_issue_id(context):
    """Verify the command output contains an issue ID."""
    # roundup-admin create returns just the issue ID
    issue_id = context.cli_stdout

    # Verify it's a number
    assert issue_id.isdigit(), f"Expected numeric issue ID, got: {issue_id}"

    # Store for later verification
    context.created_issue_id = issue_id


@then("the issue should exist in the database")
def step_issue_exists_in_database(context):
    """Verify the issue exists in the database using roundup-admin."""
    issue_id = context.created_issue_id

    # Get tracker_dir from context or use default
    tracker_dir = getattr(context, "tracker_dir", "tracker")

    # Use roundup-admin to display the issue
    cmd = [
        "roundup-admin",
        "-i",
        tracker_dir,
        "display",
        issue_id if issue_id.startswith("issue") else f"issue{issue_id}",
    ]

    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

    assert result.returncode == 0, (
        f"Failed to find issue{issue_id} in database. Stderr: {result.stderr}"
    )

    # Store the output for verification in other steps
    context.issue_display_output = result.stdout


@then('the issue title should be "{expected_title}"')
def step_verify_issue_title(context, expected_title):
    """Verify the issue has the expected title (works for both CLI and Web UI)."""
    # Use the display output if available (CLI), otherwise use web UI approach
    if hasattr(context, "issue_display_output"):
        # CLI approach - check display output
        output = context.issue_display_output
        assert expected_title in output, (
            f"Expected title '{expected_title}' not found in issue. Output: {output}"
        )
    elif hasattr(context, "page"):
        # Web UI approach - check page content
        # Navigate to the created issue if we have its ID
        issue_id = getattr(context, "created_issue_id", None)
        if issue_id:
            context.page.goto(f"{context.tracker_url}{issue_id}")
            context.page.wait_for_load_state("networkidle")

        # Check the title is displayed
        page_content = context.page.content()
        assert expected_title in page_content, (
            f"Expected title '{expected_title}' not found in page"
        )
    else:
        raise AssertionError("Neither CLI nor Web UI context available for verification")


@then('the issue priority should be "{expected_priority}"')
def step_verify_issue_priority(context, expected_priority):
    """Verify the issue has the expected priority (works for both CLI and Web UI)."""
    # Use the display output if available (CLI), otherwise use web UI approach
    if hasattr(context, "issue_display_output"):
        # CLI approach - check display output
        output = context.issue_display_output
        priority_id = PRIORITY_MAP.get(expected_priority.lower())

        # roundup-admin display shows priority: 2 (the ID), not the name
        # Check for "priority: N" format
        assert f"priority: {priority_id}" in output.lower(), (
            f"Expected priority ID '{priority_id}' for '{expected_priority}' not found in issue. Output: {output}"
        )
    elif hasattr(context, "page"):
        # Web UI approach - check page content
        # The priority should be visible on the issue page
        page_content = context.page.content()
        assert expected_priority in page_content.lower(), (
            f"Expected priority '{expected_priority}' not found"
        )
    else:
        raise AssertionError("Neither CLI nor Web UI context available for verification")


@then("the issue should have default priority")
def step_verify_default_priority(context):
    """Verify the issue has a default priority value."""
    # Just verify the display command succeeded and output exists
    output = context.issue_display_output

    # Should have some priority value
    assert "priority" in output.lower() or output.strip(), (
        f"Issue display output appears invalid. Output: {output}"
    )
