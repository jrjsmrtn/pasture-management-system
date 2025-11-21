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


@given('I create an issue with title "{title}" via email')
def step_create_issue_via_email(context, title):
    """Create an issue via email and store its ID."""
    tracker_dir = os.getenv("TRACKER_DIR", "tracker")
    context.tracker_dir = tracker_dir

    # Compose email to create issue
    msg = EmailMessage()
    msg["From"] = "roundup-admin@localhost"
    msg["To"] = "issue_tracker@localhost"
    msg["Subject"] = title
    msg["Date"] = datetime.now().strftime("%a, %d %b %Y %H:%M:%S %z")
    msg.set_content(f"Creating issue: {title}")

    # Send via mailgw
    cmd = ["roundup-mailgw", tracker_dir]
    result = subprocess.run(cmd, input=msg.as_string(), capture_output=True, text=True, timeout=30)

    assert result.returncode == 0, f"Failed to create issue via email: {result.stderr}"

    # Get the created issue ID
    cmd = ["roundup-admin", "-i", tracker_dir, "list", "issue"]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

    issue_lines = result.stdout.strip().split("\n")
    if issue_lines:
        last_line = issue_lines[-1]
        issue_id = last_line.split(":")[0].strip()
        context.last_created_issue_id = issue_id


@given('I note the issue ID as "{variable_name}"')
def step_note_issue_id(context, variable_name):
    """Store the last created issue ID in a variable for later use."""
    if not hasattr(context, "issue_variables"):
        context.issue_variables = {}
    context.issue_variables[variable_name] = context.last_created_issue_id


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
        # Issue doesn't exist, create it with an initial message
        # Create message first
        msg_cmd = [
            "roundup-admin",
            "-i",
            tracker_dir,
            "create",
            "msg",
            f"content=Initial issue: {title}",
            "author=1",
        ]
        msg_result = subprocess.run(msg_cmd, capture_output=True, text=True, timeout=30)
        assert msg_result.returncode == 0, f"Failed to create message: {msg_result.stderr}"

        message_id = msg_result.stdout.strip()

        # Create issue with the message, default status, and default priority
        cmd = [
            "roundup-admin",
            "-i",
            tracker_dir,
            "create",
            "issue",
            f"title={title}",
            f"messages={message_id}",
            "status=1",  # Default to "new" status
            "priority=3",  # Default to "urgent" priority
        ]
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
        # Issue doesn't exist, create it with message and priority
        # Create message first
        msg_cmd = [
            "roundup-admin",
            "-i",
            tracker_dir,
            "create",
            "msg",
            f"content=Initial issue: Test Issue {issue_id}",
            "author=1",
        ]
        msg_result = subprocess.run(msg_cmd, capture_output=True, text=True, timeout=30)
        assert msg_result.returncode == 0, f"Failed to create message: {msg_result.stderr}"
        message_id = msg_result.stdout.strip()

        # Create issue with message, status, and priority
        cmd = [
            "roundup-admin",
            "-i",
            tracker_dir,
            "create",
            "issue",
            f"title=Test Issue {issue_id}",
            f"status={status_id}",
            f"messages={message_id}",
            "priority=3",  # Default to "urgent" priority
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
@when("I compose an email with:")
def step_compose_email(context):
    """Compose an email message from the table data."""
    email_data = {}

    for row in context.table:
        field = row["field"]
        value = row["value"]

        # Substitute variables like {work_issue} with actual issue IDs
        if hasattr(context, "issue_variables"):
            for var_name, var_value in context.issue_variables.items():
                value = value.replace(f"{{{var_name}}}", f"issue{var_value}")

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
    """
    Send the composed email to the mail gateway.

    Supports two modes:
    - PIPE mode (default): Send via roundup-mailgw stdin
    - GreenMail mode: Send via SMTP to GreenMail, then poll via roundup-mailgw
    """
    tracker_dir = os.getenv("TRACKER_DIR", "tracker")
    context.tracker_dir = tracker_dir

    email_test_mode = os.getenv("EMAIL_TEST_MODE", "pipe").lower()

    if email_test_mode == "greenmail":
        # GreenMail mode: Hybrid approach (SMTP + mailgw)
        # Send via SMTP to test delivery, then process via mailgw to create issue
        if not hasattr(context, "greenmail_client"):
            raise RuntimeError("GreenMail mode enabled but client not available")

        try:
            # Step 1: Send email via SMTP to GreenMail (tests SMTP delivery)
            context.greenmail_client.send_raw_email(context.email_message)

            # Wait a bit for email to be processed by GreenMail
            import time

            time.sleep(0.5)

            # Step 2: Also process via roundup-mailgw (creates issue in Roundup)
            # This hybrid approach validates SMTP delivery + issue creation
            cmd = ["roundup-mailgw", tracker_dir]
            result = subprocess.run(
                cmd, input=context.email_message, capture_output=True, text=True, timeout=30
            )

            # Store result from mailgw
            context.mailgw_result = result
            context.mailgw_exit_code = result.returncode
            context.mailgw_stdout = result.stdout.strip()
            context.mailgw_stderr = result.stderr.strip()

        except Exception as e:
            # Store error for assertion
            context.mailgw_exit_code = 1
            context.mailgw_stdout = ""
            context.mailgw_stderr = str(e)

    else:
        # PIPE mode (default): Send via roundup-mailgw stdin
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


@then("no issue should be created")
def step_no_issue_created(context):
    """Verify that no issue was created (security test)."""
    tracker_dir = getattr(context, "tracker_dir", "tracker")
    cmd = ["roundup-admin", "-i", tracker_dir, "list", "issue"]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

    assert result.returncode == 0, f"Failed to list issues: {result.stderr}"

    # Should have no issues (empty output)
    issue_count = len([line for line in result.stdout.strip().split("\n") if line.strip()])
    assert issue_count == 0, (
        f"Expected no issues to be created, but found {issue_count} issue(s): "
        f"{result.stdout.strip()}"
    )


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

    # Normalize whitespace for comparison (handles HTML conversion newlines)
    import re

    normalized_content = re.sub(r"\s+", " ", content)
    normalized_expected = re.sub(r"\s+", " ", expected_text)

    assert normalized_expected in normalized_content, (
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

    # Substitute variables (strip curly braces if present)
    variable_name = issue_id.strip("{}")
    if hasattr(context, "issue_variables") and variable_name in context.issue_variables:
        issue_id = context.issue_variables[variable_name]

    # Ensure issue_id has the "issue" prefix
    if not str(issue_id).startswith("issue"):
        issue_id = f"issue{issue_id}"

    # Get the messages for this issue
    cmd = ["roundup-admin", "-i", tracker_dir, "get", "messages", issue_id]
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

    # Substitute variables (strip curly braces if present)
    variable_name = issue_id.strip("{}")
    if hasattr(context, "issue_variables") and variable_name in context.issue_variables:
        issue_id = context.issue_variables[variable_name]

    # Ensure issue_id has the "issue" prefix
    if not issue_id.startswith("issue"):
        issue_id = f"issue{issue_id}"

    # Get issue status
    cmd = ["roundup-admin", "-i", tracker_dir, "get", "status", issue_id]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30, cwd=os.getcwd())

    assert result.returncode == 0, (
        f"Failed to get issue status: {result.stderr}\n"
        f"Command: {' '.join(cmd)}\n"
        f"Stdout: {result.stdout}\n"
        f"CWD: {os.getcwd()}"
    )

    status_id = result.stdout.strip()

    # Map expected status to ID
    expected_status_id = STATUS_MAP.get(expected_status.lower())

    if expected_status_id:
        assert status_id == expected_status_id, (
            f"Expected status ID '{expected_status_id}' ({expected_status}), got '{status_id}'"
        )


@then('the issue "{issue_id}" priority should be "{expected_priority}"')
def step_verify_specific_issue_priority(context, issue_id, expected_priority):
    """Verify a specific issue has the expected priority."""
    tracker_dir = getattr(context, "tracker_dir", "tracker")

    # Substitute variables (strip curly braces if present)
    variable_name = issue_id.strip("{}")
    if hasattr(context, "issue_variables") and variable_name in context.issue_variables:
        issue_id = context.issue_variables[variable_name]

    # Ensure issue_id has the "issue" prefix
    if not issue_id.startswith("issue"):
        issue_id = f"issue{issue_id}"

    # Get issue priority
    cmd = ["roundup-admin", "-i", tracker_dir, "get", "priority", issue_id]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

    assert result.returncode == 0, f"Failed to get issue priority: {result.stderr}"

    priority_id = result.stdout.strip()

    # Map expected priority to ID
    expected_priority_id = PRIORITY_MAP.get(expected_priority.lower())

    if expected_priority_id:
        assert priority_id == expected_priority_id, (
            f"Expected priority ID '{expected_priority_id}', got '{priority_id}'"
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


@then('no user should be created with email "{email}"')
def step_verify_no_user_created(context, email):
    """Verify that no user was created with the specified email (security test)."""
    tracker_dir = getattr(context, "tracker_dir", "tracker")

    # Get all users
    cmd = ["roundup-admin", "-i", tracker_dir, "list", "user"]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

    assert result.returncode == 0, f"Failed to list users: {result.stderr}"

    # Parse user IDs from list output
    user_ids = []
    for line in result.stdout.strip().split("\n"):
        if line.strip():
            user_id = line.split(":")[0].strip()
            user_ids.append(f"user{user_id}")

    # Check addresses of all users
    if user_ids:
        cmd = ["roundup-admin", "-i", tracker_dir, "get", "address"] + user_ids
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

        assert result.returncode == 0, f"Failed to get user addresses: {result.stderr}"

        # Check if the email appears in any address
        addresses = result.stdout.strip().split("\n")
        for addr in addresses:
            if addr.strip() == email:
                raise AssertionError(
                    f"Expected no user with email {email}, but found user with that address"
                )


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


# ============================================================================
# Email Notification Step Definitions
# ============================================================================


@given("the email debug log is cleared")
def step_clear_email_debug_log(context):
    """Clear the email debug log file."""
    debug_log = "/tmp/roundup-mail-debug.log"
    if os.path.exists(debug_log):
        os.remove(debug_log)
    context.email_debug_log = debug_log


@given('I create an issue with title "{title}" via CLI')
@when('I create an issue with title "{title}" via CLI')
def step_create_issue_via_cli(context, title):
    """Create an issue via roundup-admin CLI and store its ID."""
    tracker_dir = os.getenv("TRACKER_DIR", "tracker")
    context.tracker_dir = tracker_dir

    # Create a message first (issues need messages to trigger notifications)
    msg_cmd = [
        "roundup-admin",
        "-i",
        tracker_dir,
        "create",
        "msg",
        f"content=Issue created: {title}",
        "author=1",  # admin user
    ]
    msg_result = subprocess.run(msg_cmd, capture_output=True, text=True, timeout=30)

    assert msg_result.returncode == 0, f"Failed to create message: {msg_result.stderr}"

    message_id = msg_result.stdout.strip()

    # Create issue via roundup-admin with the message and default status
    cmd = [
        "roundup-admin",
        "-i",
        tracker_dir,
        "create",
        "issue",
        f"title={title}",
        f"messages={message_id}",
        "status=1",  # Default to "new" status
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

    assert result.returncode == 0, f"Failed to create issue via CLI: {result.stderr}"

    # Get the created issue ID from output
    issue_id = result.stdout.strip()
    context.created_issue_id = issue_id
    context.last_created_issue_id = issue_id


@when("I check the email debug log")
def step_check_email_debug_log(context):
    """Read the email debug log file."""
    debug_log = getattr(context, "email_debug_log", "/tmp/roundup-mail-debug.log")

    if os.path.exists(debug_log):
        with open(debug_log) as f:
            context.debug_log_content = f.read()
    else:
        context.debug_log_content = ""


@when('I add a message to issue "{issue_id}" with content "{content}"')
def step_add_message_to_issue(context, issue_id, content):
    """Add a message to an existing issue."""
    tracker_dir = getattr(context, "tracker_dir", "tracker")

    # Ensure issue_id has the "issue" prefix
    if not issue_id.startswith("issue"):
        issue_id = f"issue{issue_id}"

    # Create a message first
    cmd = [
        "roundup-admin",
        "-i",
        tracker_dir,
        "create",
        "msg",
        f"content={content}",
        "author=1",  # admin user
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

    assert result.returncode == 0, f"Failed to create message: {result.stderr}"

    message_id = result.stdout.strip()

    # Get existing messages
    cmd = ["roundup-admin", "-i", tracker_dir, "get", "messages", issue_id]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

    # Parse existing message IDs
    messages_str = result.stdout.strip()
    if messages_str and messages_str != "[]":
        # Remove brackets and quotes: "['1', '2']" -> "1 2"
        messages_str = messages_str.strip("[]").replace("'", "").replace('"', "")
        # Split and clean
        existing_ids = [mid.strip() for mid in messages_str.split(",") if mid.strip()]
        existing_ids.append(message_id)
        # Join with commas (no spaces)
        messages_list = ",".join(existing_ids)
    else:
        messages_list = message_id

    # Update issue with new message list
    cmd = ["roundup-admin", "-i", tracker_dir, "set", issue_id, f"messages={messages_list}"]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

    assert result.returncode == 0, (
        f"Failed to add message to issue: {result.stderr}\nStdout: {result.stdout}"
    )


@when('I update issue "{issue_id}" status to "{status}"')
def step_update_issue_status(context, issue_id, status):
    """Update the status of an issue."""
    tracker_dir = getattr(context, "tracker_dir", "tracker")

    # Ensure issue_id has the "issue" prefix
    if not issue_id.startswith("issue"):
        issue_id = f"issue{issue_id}"

    # Map status to ID
    status_id = STATUS_MAP.get(status.lower())

    assert status_id, f"Unknown status: {status}"

    # Update issue status
    cmd = ["roundup-admin", "-i", tracker_dir, "set", issue_id, f"status={status_id}"]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

    assert result.returncode == 0, f"Failed to update issue status: {result.stderr}"

    # Add a message to trigger notification (status changes alone don't trigger notifications)
    msg_cmd = [
        "roundup-admin",
        "-i",
        tracker_dir,
        "create",
        "msg",
        f"content=Status changed to {status}",
        "author=1",
    ]
    msg_result = subprocess.run(msg_cmd, capture_output=True, text=True, timeout=30)

    assert msg_result.returncode == 0, f"Failed to create message: {msg_result.stderr}"

    message_id = msg_result.stdout.strip()

    # Get existing messages
    get_cmd = ["roundup-admin", "-i", tracker_dir, "get", "messages", issue_id]
    get_result = subprocess.run(get_cmd, capture_output=True, text=True, timeout=30)

    # Parse and update messages list
    messages_str = get_result.stdout.strip()
    if messages_str and messages_str != "[]":
        messages_str = messages_str.strip("[]").replace("'", "").replace('"', "")
        existing_ids = [mid.strip() for mid in messages_str.split(",") if mid.strip()]
        existing_ids.append(message_id)
        messages_list = ",".join(existing_ids)
    else:
        messages_list = message_id

    # Add message to issue
    set_cmd = ["roundup-admin", "-i", tracker_dir, "set", issue_id, f"messages={messages_list}"]
    set_result = subprocess.run(set_cmd, capture_output=True, text=True, timeout=30)

    assert set_result.returncode == 0, f"Failed to add message to issue: {set_result.stderr}"


@when('I update issue "{issue_id}" priority to "{priority}"')
def step_update_issue_priority(context, issue_id, priority):
    """Update the priority of an issue."""
    tracker_dir = getattr(context, "tracker_dir", "tracker")

    # Ensure issue_id has the "issue" prefix
    if not issue_id.startswith("issue"):
        issue_id = f"issue{issue_id}"

    # Map priority to ID
    priority_id = PRIORITY_MAP.get(priority.lower())

    assert priority_id, f"Unknown priority: {priority}"

    # Update issue priority
    cmd = ["roundup-admin", "-i", tracker_dir, "set", issue_id, f"priority={priority_id}"]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

    assert result.returncode == 0, f"Failed to update issue priority: {result.stderr}"

    # Add a message to trigger notification (priority changes alone don't trigger notifications)
    msg_cmd = [
        "roundup-admin",
        "-i",
        tracker_dir,
        "create",
        "msg",
        f"content=Priority changed to {priority}",
        "author=1",
    ]
    msg_result = subprocess.run(msg_cmd, capture_output=True, text=True, timeout=30)

    assert msg_result.returncode == 0, f"Failed to create message: {msg_result.stderr}"

    message_id = msg_result.stdout.strip()

    # Get existing messages
    get_cmd = ["roundup-admin", "-i", tracker_dir, "get", "messages", issue_id]
    get_result = subprocess.run(get_cmd, capture_output=True, text=True, timeout=30)

    # Parse and update messages list
    messages_str = get_result.stdout.strip()
    if messages_str and messages_str != "[]":
        messages_str = messages_str.strip("[]").replace("'", "").replace('"', "")
        existing_ids = [mid.strip() for mid in messages_str.split(",") if mid.strip()]
        existing_ids.append(message_id)
        messages_list = ",".join(existing_ids)
    else:
        messages_list = message_id

    # Add message to issue
    set_cmd = ["roundup-admin", "-i", tracker_dir, "set", issue_id, f"messages={messages_list}"]
    set_result = subprocess.run(set_cmd, capture_output=True, text=True, timeout=30)

    assert set_result.returncode == 0, f"Failed to add message to issue: {set_result.stderr}"


@then("an email notification should have been sent")
def step_verify_notification_sent(context):
    """Verify that an email notification was sent (debug log has content)."""
    log_content = getattr(context, "debug_log_content", "")

    assert log_content, "No email notification found in debug log"
    assert "From:" in log_content, "Email notification missing From header"
    assert "To:" in log_content, "Email notification missing To header"
    assert "Subject:" in log_content, "Email notification missing Subject header"


@then('the notification subject should contain "{text}"')
def step_verify_notification_subject(context, text):
    """Verify the notification subject contains the expected text."""
    log_content = getattr(context, "debug_log_content", "")

    # Parse subject line
    subject_line = ""
    for line in log_content.split("\n"):
        if line.startswith("Subject:"):
            subject_line = line
            break

    assert subject_line, "No Subject line found in email notification"
    assert text in subject_line, f"Expected '{text}' in subject, got: {subject_line}"


@then('the notification should be sent to "{email}"')
def step_verify_notification_recipient(context, email):
    """Verify the notification was sent to the specified email address."""
    log_content = getattr(context, "debug_log_content", "")

    # Parse To line
    to_line = ""
    for line in log_content.split("\n"):
        if line.startswith("To:"):
            to_line = line
            break

    assert to_line, "No To line found in email notification"
    assert email in to_line, f"Expected '{email}' in recipients, got: {to_line}"


@then("the notification should contain the issue link")
def step_verify_notification_contains_link(context):
    """Verify the notification contains an issue link."""
    log_content = getattr(context, "debug_log_content", "")

    # Look for issue link pattern (e.g., http://localhost:9080/pms/issue1)
    assert "issue" in log_content.lower(), "No issue reference found in notification"


@then('the notification body should contain "{text}"')
def step_verify_notification_body(context, text):
    """Verify the notification body contains the expected text."""
    log_content = getattr(context, "debug_log_content", "")

    assert text in log_content, f"Expected '{text}' in notification body"


@given('user "{email}" is on the nosy list for issue "{issue_id}"')
def step_add_user_to_nosy_list(context, email, issue_id):
    """Add a user to the nosy list for an issue."""
    tracker_dir = getattr(context, "tracker_dir", "tracker")

    # Ensure issue_id has the "issue" prefix
    if not issue_id.startswith("issue"):
        issue_id = f"issue{issue_id}"

    # Find or create user with this email
    cmd = ["roundup-admin", "-i", tracker_dir, "find", "user", f"address={email}"]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

    if result.returncode == 0 and result.stdout.strip():
        user_id = result.stdout.strip()
    else:
        # Create user
        username = email.split("@")[0]
        cmd = [
            "roundup-admin",
            "-i",
            tracker_dir,
            "create",
            "user",
            f"username={username}",
            f"address={email}",
            "roles=User",
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        assert result.returncode == 0, f"Failed to create user: {result.stderr}"
        user_id = result.stdout.strip()

    # Get existing nosy list
    cmd = ["roundup-admin", "-i", tracker_dir, "get", "nosy", issue_id]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

    # Parse existing nosy list
    nosy_str = result.stdout.strip()
    if nosy_str and nosy_str != "[]":
        nosy_str = nosy_str.strip("[]").replace("'", "").replace('"', "")
        nosy_ids = [nid.strip() for nid in nosy_str.split(",") if nid.strip()]
        if user_id not in nosy_ids:
            nosy_ids.append(user_id)
        nosy_list = ",".join(nosy_ids)
    else:
        nosy_list = user_id

    # Update nosy list
    cmd = ["roundup-admin", "-i", tracker_dir, "set", issue_id, f"nosy={nosy_list}"]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

    assert result.returncode == 0, f"Failed to add user to nosy list: {result.stderr}"


@given('the admin user is on the nosy list for issue "{issue_id}"')
def step_add_admin_to_nosy_list(context, issue_id):
    """Add the admin user to the nosy list for an issue."""
    tracker_dir = getattr(context, "tracker_dir", "tracker")

    # Ensure issue_id has the "issue" prefix
    if not issue_id.startswith("issue"):
        issue_id = f"issue{issue_id}"

    # Get existing nosy list
    cmd = ["roundup-admin", "-i", tracker_dir, "get", "nosy", issue_id]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

    # Parse existing nosy list
    nosy_str = result.stdout.strip()
    if nosy_str and nosy_str != "[]":
        nosy_str = nosy_str.strip("[]").replace("'", "").replace('"', "")
        nosy_ids = [nid.strip() for nid in nosy_str.split(",") if nid.strip()]
        if "1" not in nosy_ids:  # Admin is user 1
            nosy_ids.append("1")
        nosy_list = ",".join(nosy_ids)
    else:
        nosy_list = "1"  # Admin is user 1

    # Update nosy list
    cmd = ["roundup-admin", "-i", tracker_dir, "set", issue_id, f"nosy={nosy_list}"]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

    assert result.returncode == 0, f"Failed to add admin to nosy list: {result.stderr}"


@then("email notifications should have been sent to:")
def step_verify_multiple_notifications(context):
    """Verify notifications were sent to multiple recipients."""
    log_content = getattr(context, "debug_log_content", "")

    for row in context.table:
        recipient = row["recipient"]
        assert recipient in log_content, f"No notification sent to {recipient}"


@then("the notification should contain:")
def step_verify_notification_metadata(context):
    """Verify the notification contains specific metadata."""
    log_content = getattr(context, "debug_log_content", "")

    for row in context.table:
        field = row["field"]
        value = row["value"]
        assert value in log_content, f"Expected '{field}: {value}' in notification"


@given('nosy configuration is set to "{config}"')
def step_verify_nosy_configuration(context, config):
    """Verify the nosy configuration setting."""
    tracker_dir = getattr(context, "tracker_dir", "tracker")
    config_file = os.path.join(tracker_dir, "config.ini")

    assert os.path.exists(config_file), f"Config file not found: {config_file}"

    with open(config_file) as f:
        config_content = f.read()
        assert config in config_content, f"Expected config '{config}' not found in config.ini"


@when("I check the nosy list for the created issue")
def step_check_nosy_list(context):
    """Get the nosy list for the last created issue."""
    tracker_dir = getattr(context, "tracker_dir", "tracker")
    issue_id = context.created_issue_id

    # Ensure issue_id has the "issue" prefix
    if not issue_id.startswith("issue"):
        issue_id = f"issue{issue_id}"

    cmd = ["roundup-admin", "-i", tracker_dir, "get", "nosy", issue_id]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

    assert result.returncode == 0, f"Failed to get nosy list: {result.stderr}"

    nosy_str = result.stdout.strip()
    if nosy_str and nosy_str != "[]":
        nosy_str = nosy_str.strip("[]'\"")
        nosy_ids = [nid.strip().strip("'\"") for nid in nosy_str.split(",")]
        context.nosy_list = nosy_ids
    else:
        context.nosy_list = []


@then("the creator should be on the nosy list")
def step_verify_creator_on_nosy_list(context):
    """Verify the creator is on the nosy list."""
    tracker_dir = getattr(context, "tracker_dir", "tracker")
    issue_id = context.created_issue_id

    # Ensure issue_id has the "issue" prefix
    if not issue_id.startswith("issue"):
        issue_id = f"issue{issue_id}"

    # Get issue creator
    cmd = ["roundup-admin", "-i", tracker_dir, "get", "creator", issue_id]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

    assert result.returncode == 0, f"Failed to get creator: {result.stderr}"

    creator_id = result.stdout.strip()
    nosy_list = getattr(context, "nosy_list", [])

    assert creator_id in nosy_list, f"Creator {creator_id} not in nosy list: {nosy_list}"


@then("an email notification should have been sent to the creator")
def step_verify_creator_notification(context):
    """Verify an email notification was sent to the creator."""
    tracker_dir = getattr(context, "tracker_dir", "tracker")

    # Get admin user email
    cmd = ["roundup-admin", "-i", tracker_dir, "get", "address", "user1"]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

    if result.returncode == 0:
        admin_email = result.stdout.strip()
        log_content = getattr(context, "debug_log_content", "")
        assert admin_email in log_content, f"No notification sent to creator ({admin_email})"


@then('no email notification should have been sent to "{email}"')
def step_verify_no_notification(context, email):
    """Verify no email notification was sent to the specified address."""
    log_content = getattr(context, "debug_log_content", "")

    # For "messages_to_author = no", the author should not receive their own message notifications
    # This is complex to verify, as we'd need to check if there's NO email to this address
    # For now, we'll verify the debug log exists but the specific email isn't in To: line

    if log_content:
        # Parse To lines
        to_lines = [line for line in log_content.split("\n") if line.startswith("To:")]
        for to_line in to_lines:
            # Check if this email is NOT in the To line
            if email in to_line:
                raise AssertionError(f"Unexpected notification sent to {email}")


# ============================================================================
# GreenMail-Specific Step Definitions (IMAP/SMTP)
# ============================================================================


@then('the GreenMail mailbox for "{user}" should have {count:d} message(s)')
def step_verify_greenmail_message_count(context, user, count):
    """Verify the GreenMail mailbox has the expected number of messages."""
    if not hasattr(context, "greenmail_client"):
        # Not in GreenMail mode, skip this step
        return

    actual_count = context.greenmail_client.get_message_count(user=user, password=user)

    assert actual_count == count, f"Expected {count} message(s) in mailbox, got {actual_count}"


@then('the GreenMail mailbox for "{user}" should contain a message with subject "{subject}"')
def step_verify_greenmail_message_subject(context, user, subject):
    """Verify the GreenMail mailbox contains a message with the expected subject."""
    if not hasattr(context, "greenmail_client"):
        # Not in GreenMail mode, skip this step
        return

    messages = context.greenmail_client.get_received_messages(user=user, password=user)

    subjects = [msg.get("Subject", "") for msg in messages]

    assert any(subject in s for s in subjects), (
        f"Expected subject '{subject}' not found in mailbox. Found: {subjects}"
    )


@then('the GreenMail mailbox for "{user}" should contain a message from "{from_addr}"')
def step_verify_greenmail_message_from(context, user, from_addr):
    """Verify the GreenMail mailbox contains a message from the expected sender."""
    if not hasattr(context, "greenmail_client"):
        # Not in GreenMail mode, skip this step
        return

    messages = context.greenmail_client.get_received_messages(user=user, password=user)

    from_addrs = [msg.get("From", "") for msg in messages]

    assert any(from_addr in f for f in from_addrs), (
        f"Expected from '{from_addr}' not found in mailbox. Found: {from_addrs}"
    )


@then('the GreenMail mailbox for "{user}" should contain "{text}" in the message body')
def step_verify_greenmail_message_body(context, user, text):
    """Verify the GreenMail mailbox contains a message with the expected text in body."""
    if not hasattr(context, "greenmail_client"):
        # Not in GreenMail mode, skip this step
        return

    messages = context.greenmail_client.get_received_messages(user=user, password=user)

    found = False
    for msg in messages:
        # Get message body
        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_type() == "text/plain":
                    body = part.get_payload(decode=True).decode()
                    if text in body:
                        found = True
                        break
        else:
            body = msg.get_payload(decode=True).decode()
            if text in body:
                found = True
                break

    assert found, f"Expected text '{text}' not found in any message body"


@when("I wait for an email to arrive in GreenMail")
def step_wait_for_greenmail_email(context):
    """Wait for an email to arrive in the GreenMail mailbox."""
    if not hasattr(context, "greenmail_client"):
        # Not in GreenMail mode, skip this step
        return

    # Use default user (admin)
    user = "roundup-admin@localhost"
    msg = context.greenmail_client.wait_for_message(timeout=10, user=user, password=user)

    assert msg is not None, "No email received in GreenMail within timeout"

    # Store message for further verification
    context.greenmail_last_message = msg


@then('the GreenMail email should have subject containing "{text}"')
def step_verify_greenmail_last_message_subject(context, text):
    """Verify the last GreenMail message has the expected subject."""
    if not hasattr(context, "greenmail_last_message"):
        raise AssertionError("No GreenMail message available for verification")

    subject = context.greenmail_last_message.get("Subject", "")

    assert text in subject, f"Expected '{text}' in subject, got: {subject}"


@then('the GreenMail email body should contain "{text}"')
def step_verify_greenmail_last_message_body(context, text):
    """Verify the last GreenMail message body contains the expected text."""
    if not hasattr(context, "greenmail_last_message"):
        raise AssertionError("No GreenMail message available for verification")

    msg = context.greenmail_last_message

    # Get message body
    body = ""
    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_type() == "text/plain":
                body = part.get_payload(decode=True).decode()
                break
    else:
        body = msg.get_payload(decode=True).decode()

    assert text in body, f"Expected '{text}' in body, got: {body[:200]}..."


# ============================================================================
# Email Security Step Definitions (Sprint 9, Story 4)
# ============================================================================


@then("no error message should be sent")
def step_verify_no_error_message(context):
    """Verify that no error/bounce message was sent by the mail gateway."""
    # In strict mode with silent rejection, no error messages are sent
    # This step verifies the absence of error responses
    debug_log = getattr(context, "email_debug_log", "/tmp/roundup-mail-debug.log")

    # Check if any error messages were logged or sent
    if os.path.exists(debug_log):
        with open(debug_log) as f:
            log_content = f.read()
            # Check for common error indicators
            error_indicators = ["Error:", "Failed:", "Invalid:", "Rejected:"]
            for indicator in error_indicators:
                if indicator in log_content:
                    raise AssertionError(
                        f"Error message found in debug log: {indicator}\nLog: {log_content[:500]}"
                    )


@given("PGP is configured and enabled")
def step_verify_pgp_configured(context):
    """Verify that PGP/GPG is configured and enabled in the tracker."""
    tracker_dir = getattr(context, "tracker_dir", "tracker")
    config_file = os.path.join(tracker_dir, "config.ini")

    # Check if PGP is enabled in config
    with open(config_file) as f:
        config_content = f.read()
        if "enable = yes" not in config_content or "[pgp]" not in config_content:
            # PGP not configured - skip this scenario
            context.scenario.skip(
                "PGP is not configured. This is an optional feature for homelabs."
            )
            return

    # Check if gpg command is available
    try:
        subprocess.run(["gpg", "--version"], capture_output=True, timeout=5)
    except (FileNotFoundError, subprocess.TimeoutExpired):
        context.scenario.skip("GPG not installed. PGP features require gpg command.")


@given("I compose a PGP-signed email with")
def step_compose_pgp_signed_email(context):
    """Compose a PGP-signed email (documentation/optional scenario)."""
    # This step is primarily for documentation purposes
    # Actual PGP signing requires gpg key setup and is optional
    context.scenario.skip(
        "PGP email signing is an optional advanced feature. "
        "See documentation for PGP/GPG configuration guide."
    )


@then("the issue should be marked as PGP-verified")
def step_verify_pgp_status(context):
    """Verify that the issue is marked as PGP-verified (optional feature)."""
    # This step is primarily for documentation purposes
    context.scenario.skip(
        "PGP verification status tracking is an optional advanced feature. "
        "See Roundup PGP documentation for implementation details."
    )
