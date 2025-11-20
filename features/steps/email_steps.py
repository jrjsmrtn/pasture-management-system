# SPDX-FileCopyrightText: 2025 Georges Martin <jrjsmrtn@gmail.com>
# SPDX-License-Identifier: MIT

"""Step definitions for email gateway interactions with Roundup tracker."""

import os
import subprocess
from datetime import datetime
from email import encoders
from email.message import EmailMessage
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from behave import given, then, when

from features.steps.common import PRIORITY_MAP, STATUS_MAP


@given('the admin user exists with email "{email}"')
def step_admin_user_exists(context, email):
    """Verify admin user exists with the specified email."""
    tracker_dir = os.getenv("TRACKER_DIR", "tracker")
    context.tracker_dir = tracker_dir

    # Query for users to ensure database is accessible
    cmd = ["roundup-admin", "-i", tracker_dir, "list", "user"]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

    assert result.returncode == 0, f"Failed to access user database: {result.stderr}"
    assert "admin" in result.stdout.lower(), "Admin user not found in user list"

    # Store admin email in context
    context.admin_email = email


@given('no user exists with email "{email}"')
def step_no_user_exists(context, email):
    """Verify that no user exists with the specified email."""
    tracker_dir = os.getenv("TRACKER_DIR", "tracker")
    context.tracker_dir = tracker_dir

    # Query for users with this email
    cmd = ["roundup-admin", "-i", tracker_dir, "find", "user", f"address={email}"]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

    # If user exists, remove them for test isolation
    if result.returncode == 0 and result.stdout.strip():
        user_id = result.stdout.strip()
        cmd = ["roundup-admin", "-i", tracker_dir, "retire", "user", user_id]
        subprocess.run(cmd, capture_output=True, text=True, timeout=30)


@given('an issue exists with id "{issue_id}" and title "{title}"')
def step_issue_exists_with_title(context, issue_id, title):
    """Verify or create an issue with the specified ID and title."""
    tracker_dir = os.getenv("TRACKER_DIR", "tracker")
    context.tracker_dir = tracker_dir

    # Try to get the issue
    cmd = ["roundup-admin", "-i", tracker_dir, "get", "title", f"issue{issue_id}"]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

    if result.returncode != 0:
        # Issue doesn't exist, create it
        cmd = ["roundup-admin", "-i", tracker_dir, "create", "issue", f"title={title}"]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        assert result.returncode == 0, f"Failed to create issue: {result.stderr}"

    # Store issue ID for later verification
    context.existing_issue_id = issue_id


@given('an issue exists with id "{issue_id}" and status "{status}"')
def step_issue_exists_with_status(context, issue_id, status):
    """Verify or create an issue with the specified ID and status."""
    tracker_dir = os.getenv("TRACKER_DIR", "tracker")
    context.tracker_dir = tracker_dir

    # Map status to ID
    status_id = STATUS_MAP.get(status.lower(), "1")

    # Try to get the issue
    cmd = ["roundup-admin", "-i", tracker_dir, "get", "status", f"issue{issue_id}"]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

    if result.returncode != 0:
        # Issue doesn't exist, create it
        cmd = [
            "roundup-admin",
            "-i",
            tracker_dir,
            "create",
            "issue",
            f"title=Test Issue {issue_id}",
            f"status={status_id}",
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        assert result.returncode == 0, f"Failed to create issue: {result.stderr}"
    else:
        # Update the status
        cmd = ["roundup-admin", "-i", tracker_dir, "set", f"issue{issue_id}", f"status={status_id}"]
        subprocess.run(cmd, capture_output=True, text=True, timeout=30)

    # Store issue ID for later verification
    context.existing_issue_id = issue_id
    context.original_status = status


@given("I compose an email with:")
def step_compose_email(context):
    """Compose an email message from the table data."""
    email_data = {}

    for row in context.table:
        field = row["field"]
        value = row["value"]
        email_data[field] = value

    # Create email message
    msg = EmailMessage()
    msg["From"] = email_data.get("from", "test@localhost")
    msg["To"] = email_data.get("to", "issue_tracker@localhost")
    msg["Subject"] = email_data.get("subject", "Test Subject")
    msg["Date"] = datetime.now().strftime("%a, %d %b %Y %H:%M:%S %z")

    # Set body
    body = email_data.get("body", "")
    # Handle newlines in body
    body = body.replace("\\n", "\n")
    msg.set_content(body)

    # Store email data and message
    context.email_data = email_data
    context.email_message = msg.as_string()


@given("I compose an HTML email with:")
def step_compose_html_email(context):
    """Compose an HTML email message from the table data."""
    email_data = {}

    for row in context.table:
        field = row["field"]
        value = row["value"]
        email_data[field] = value

    # Create multipart email message
    msg = MIMEMultipart("alternative")
    msg["From"] = email_data.get("from", "test@localhost")
    msg["To"] = email_data.get("to", "issue_tracker@localhost")
    msg["Subject"] = email_data.get("subject", "Test Subject")
    msg["Date"] = datetime.now().strftime("%a, %d %b %Y %H:%M:%S %z")

    # Add HTML part
    html_content = email_data.get("html", "<p>Test HTML</p>")
    html_part = MIMEText(html_content, "html")
    msg.attach(html_part)

    # Store email data and message
    context.email_data = email_data
    context.email_message = msg.as_string()


@when("I send the email to the mail gateway")
def step_send_email_to_gateway(context):
    """Send the composed email to the roundup-mailgw via PIPE."""
    tracker_dir = os.getenv("TRACKER_DIR", "tracker")
    context.tracker_dir = tracker_dir

    # Use roundup-mailgw in PIPE mode (reads from stdin)
    cmd = ["roundup-mailgw", tracker_dir]

    # Send email via stdin
    result = subprocess.run(
        cmd, input=context.email_message, capture_output=True, text=True, timeout=30
    )

    # Store result
    context.mailgw_result = result
    context.mailgw_exit_code = result.returncode
    context.mailgw_stdout = result.stdout.strip()
    context.mailgw_stderr = result.stderr.strip()


@then("a new issue should be created")
def step_new_issue_created(context):
    """Verify a new issue was created."""
    # Check that mailgw succeeded
    assert context.mailgw_exit_code == 0, (
        f"Mail gateway failed with exit code {context.mailgw_exit_code}. "
        f"Stdout: {context.mailgw_stdout}. Stderr: {context.mailgw_stderr}"
    )

    # Get the last created issue ID
    tracker_dir = getattr(context, "tracker_dir", "tracker")
    cmd = ["roundup-admin", "-i", tracker_dir, "list", "issue"]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

    assert result.returncode == 0, f"Failed to list issues: {result.stderr}"

    # Parse issue IDs (format: "1: title", "2: title", etc.)
    issue_lines = result.stdout.strip().split("\n")
    if issue_lines:
        last_line = issue_lines[-1]
        issue_id = last_line.split(":")[0].strip()
        context.created_issue_id = issue_id
        # Also set current_issue_id for compatibility with other step definitions
        context.current_issue_id = f"issue{issue_id}"

        # Get issue display output for verification steps
        cmd = ["roundup-admin", "-i", tracker_dir, "display", f"issue{issue_id}"]
        display_result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if display_result.returncode == 0:
            context.issue_display_output = display_result.stdout
    else:
        raise AssertionError("No issues found in database")


@then('the issue description should contain "{expected_text}"')
def step_verify_issue_description(context, expected_text):
    """Verify the issue description contains the expected text."""
    issue_id = context.created_issue_id
    tracker_dir = getattr(context, "tracker_dir", "tracker")

    # Get the messages for this issue
    cmd = ["roundup-admin", "-i", tracker_dir, "get", "messages", f"issue{issue_id}"]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

    assert result.returncode == 0, f"Failed to get issue messages: {result.stderr}"

    # Parse message IDs (format: "['1', '2']")
    message_ids_str = result.stdout.strip()
    if not message_ids_str or message_ids_str == "[]":
        raise AssertionError("No messages found for issue")

    # Extract message IDs from the list format
    message_ids_str = message_ids_str.strip("[]'\"")
    message_ids = [mid.strip().strip("'\"") for mid in message_ids_str.split(",")]
    message_id = message_ids[0]

    # Get message content
    cmd = ["roundup-admin", "-i", tracker_dir, "get", "content", f"msg{message_id}"]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

    assert result.returncode == 0, f"Failed to get message content: {result.stderr}"

    content = result.stdout.strip()
    assert expected_text in content, (
        f"Expected text '{expected_text}' not found in message content: {content}"
    )


@then('the issue status should not be "{unexpected_status}"')
def step_verify_issue_status_not(context, unexpected_status):
    """Verify the issue does not have the specified status."""
    # Get issue ID from either existing_issue_id or created_issue_id
    if hasattr(context, "existing_issue_id"):
        issue_id = context.existing_issue_id
    elif hasattr(context, "created_issue_id"):
        issue_id = context.created_issue_id
    else:
        raise AssertionError("No issue ID available in context")

    tracker_dir = getattr(context, "tracker_dir", "tracker")

    # Ensure issue_id has the "issue" prefix
    if not issue_id.startswith("issue"):
        issue_id = f"issue{issue_id}"

    # Get issue status
    cmd = ["roundup-admin", "-i", tracker_dir, "get", "status", issue_id]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

    assert result.returncode == 0, f"Failed to get issue status: {result.stderr}"

    status_id = result.stdout.strip()

    # Map unexpected status to ID
    unexpected_status_id = STATUS_MAP.get(unexpected_status.lower())

    if unexpected_status_id:
        assert status_id != unexpected_status_id, (
            f"Issue should not have status '{unexpected_status}' (ID: {unexpected_status_id})"
        )


@then('the issue "{issue_id}" should have a new message')
def step_verify_issue_has_new_message(context, issue_id):
    """Verify the issue has received a new message."""
    tracker_dir = getattr(context, "tracker_dir", "tracker")

    # Get the messages for this issue
    cmd = ["roundup-admin", "-i", tracker_dir, "get", "messages", f"issue{issue_id}"]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

    assert result.returncode == 0, f"Failed to get issue messages: {result.stderr}"

    # Parse message IDs (format: "['1', '2']")
    message_ids_str = result.stdout.strip()
    assert message_ids_str and message_ids_str != "[]", f"No messages found for issue {issue_id}"

    # Extract message IDs from the list format
    message_ids_str = message_ids_str.strip("[]'\"")
    message_ids = [mid.strip().strip("'\"") for mid in message_ids_str.split(",")]

    # Store message IDs for later verification
    context.issue_message_ids = message_ids


@then('the new message should contain "{expected_text}"')
def step_verify_new_message_content(context, expected_text):
    """Verify the new message contains the expected text."""
    tracker_dir = getattr(context, "tracker_dir", "tracker")

    # Get the last message ID
    message_ids = context.issue_message_ids
    last_message_id = message_ids[-1]

    # Get message content
    cmd = ["roundup-admin", "-i", tracker_dir, "get", "content", f"msg{last_message_id}"]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

    assert result.returncode == 0, f"Failed to get message content: {result.stderr}"

    content = result.stdout.strip()
    assert expected_text in content, (
        f"Expected text '{expected_text}' not found in message content: {content}"
    )


@then('the issue "{issue_id}" status should be "{expected_status}"')
def step_verify_specific_issue_status(context, issue_id, expected_status):
    """Verify a specific issue has the expected status."""
    tracker_dir = getattr(context, "tracker_dir", "tracker")

    # Ensure issue_id has the "issue" prefix
    if not issue_id.startswith("issue"):
        issue_id = f"issue{issue_id}"

    # Get issue status
    cmd = ["roundup-admin", "-i", tracker_dir, "get", "status", issue_id]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

    assert result.returncode == 0, f"Failed to get issue status: {result.stderr}"

    status_id = result.stdout.strip()

    # Map expected status to ID
    expected_status_id = STATUS_MAP.get(expected_status.lower())

    if expected_status_id:
        assert status_id == expected_status_id, (
            f"Expected status ID '{expected_status_id}', got '{status_id}'"
        )


@then("the email should be rejected")
def step_verify_email_rejected(context):
    """Verify the email was rejected by the mail gateway."""
    # Check that mailgw failed or returned an error
    assert context.mailgw_exit_code != 0 or "error" in context.mailgw_stderr.lower(), (
        f"Expected email to be rejected, but mailgw succeeded. "
        f"Exit code: {context.mailgw_exit_code}. "
        f"Stderr: {context.mailgw_stderr}"
    )


@then("the sender should receive an error notification")
def step_verify_error_notification(context):
    """Verify the sender received an error notification."""
    # In debug mode, emails are written to /tmp/roundup-mail-debug.log
    # Check that file for error notification
    debug_log = "/tmp/roundup-mail-debug.log"

    if os.path.exists(debug_log):
        with open(debug_log) as f:
            log_content = f.read()
            assert "error" in log_content.lower() or "invalid" in log_content.lower(), (
                "Expected error notification in debug log, but not found"
            )


@then('a new user should be created with email "{email}"')
def step_verify_new_user_created(context, email):
    """Verify a new user was created with the specified email."""
    tracker_dir = getattr(context, "tracker_dir", "tracker")

    # Query for users with this email
    cmd = ["roundup-admin", "-i", tracker_dir, "find", "user", f"address={email}"]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

    assert result.returncode == 0, f"Failed to find user: {result.stderr}"
    assert result.stdout.strip(), f"User with email {email} not found"

    # Store user ID
    context.created_user_id = result.stdout.strip()


@then("the issue should be assigned to the new user")
def step_verify_issue_assigned_to_new_user(context):
    """Verify the issue was assigned to the newly created user."""
    issue_id = context.created_issue_id
    user_id = context.created_user_id
    tracker_dir = getattr(context, "tracker_dir", "tracker")

    # Ensure issue_id has the "issue" prefix
    if not issue_id.startswith("issue"):
        issue_id = f"issue{issue_id}"

    # Get issue creator
    cmd = ["roundup-admin", "-i", tracker_dir, "get", "creator", issue_id]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

    assert result.returncode == 0, f"Failed to get issue creator: {result.stderr}"

    creator_id = result.stdout.strip()
    assert creator_id == user_id, (
        f"Expected issue to be created by user {user_id}, got {creator_id}"
    )


@then("the issue should have {count:d} attachments")
def step_verify_attachment_count(context, count):
    """Verify the issue has the expected number of attachments."""
    issue_id = context.created_issue_id
    tracker_dir = getattr(context, "tracker_dir", "tracker")

    # Ensure issue_id has the "issue" prefix
    if not issue_id.startswith("issue"):
        issue_id = f"issue{issue_id}"

    # Get issue files (attachments)
    cmd = ["roundup-admin", "-i", tracker_dir, "get", "files", issue_id]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

    assert result.returncode == 0, f"Failed to get issue files: {result.stderr}"

    # Parse file IDs (format: "['1', '2']")
    files_str = result.stdout.strip()
    if files_str and files_str != "[]":
        files_str = files_str.strip("[]'\"")
        file_ids = [fid.strip().strip("'\"") for fid in files_str.split(",")]
        actual_count = len(file_ids)
    else:
        actual_count = 0

    assert actual_count == count, f"Expected {count} attachments, got {actual_count}"


@then('the attachments should be named "{name1}" and "{name2}"')
def step_verify_attachment_names(context, name1, name2):
    """Verify the attachments have the expected names."""
    issue_id = context.created_issue_id
    tracker_dir = getattr(context, "tracker_dir", "tracker")

    # Ensure issue_id has the "issue" prefix
    if not issue_id.startswith("issue"):
        issue_id = f"issue{issue_id}"

    # Get issue files (attachments)
    cmd = ["roundup-admin", "-i", tracker_dir, "get", "files", issue_id]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

    assert result.returncode == 0, f"Failed to get issue files: {result.stderr}"

    # Parse file IDs
    files_str = result.stdout.strip()
    files_str = files_str.strip("[]'\"")
    file_ids = [fid.strip().strip("'\"") for fid in files_str.split(",")]

    # Get file names
    file_names = []
    for file_id in file_ids:
        cmd = ["roundup-admin", "-i", tracker_dir, "get", "name", f"file{file_id}"]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            file_names.append(result.stdout.strip())

    expected_names = [name1, name2]
    assert set(file_names) == set(expected_names), (
        f"Expected attachments {expected_names}, got {file_names}"
    )


@then('the issue description should not contain "{unexpected_text}"')
def step_verify_description_not_contains(context, unexpected_text):
    """Verify the issue description does not contain the specified text."""
    issue_id = context.created_issue_id
    tracker_dir = getattr(context, "tracker_dir", "tracker")

    # Get the messages for this issue
    cmd = ["roundup-admin", "-i", tracker_dir, "get", "messages", f"issue{issue_id}"]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

    assert result.returncode == 0, f"Failed to get issue messages: {result.stderr}"

    # Parse message IDs
    message_ids_str = result.stdout.strip()
    if not message_ids_str or message_ids_str == "[]":
        return  # No messages, so text is not present

    # Extract message IDs from the list format
    message_ids_str = message_ids_str.strip("[]'\"")
    message_ids = [mid.strip().strip("'\"") for mid in message_ids_str.split(",")]
    message_id = message_ids[0]

    # Get message content
    cmd = ["roundup-admin", "-i", tracker_dir, "get", "content", f"msg{message_id}"]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

    assert result.returncode == 0, f"Failed to get message content: {result.stderr}"

    content = result.stdout.strip()
    assert unexpected_text not in content, (
        f"Did not expect text '{unexpected_text}' in message content, but it was found"
    )
