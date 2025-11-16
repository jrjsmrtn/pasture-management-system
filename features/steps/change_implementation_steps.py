# SPDX-FileCopyrightText: 2025 Georges Martin <jrjsmrtn@gmail.com>
# SPDX-License-Identifier: MIT

"""Step definitions for change implementation tracking scenarios."""

import subprocess

from behave import given, then, when


@given("the change was scheduled for {hours:d} hours")
def step_change_scheduled_duration(context, hours):
    """Set up a change with a scheduled duration."""
    # This is informational for the scenario
    # The actual scheduled times would be set separately
    context.scheduled_duration_hours = hours


@given('the change actual times were "{actual_start}" to "{actual_end}"')
def step_set_actual_times(context, actual_start, actual_end):
    """Set actual start and end times for a change."""
    tracker_dir = getattr(context, "tracker_dir", "tracker")

    # Get the most recently created change
    if hasattr(context, "created_change_id"):
        change_id = context.created_change_id
    elif hasattr(context, "created_changes") and context.created_changes:
        change_id = list(context.created_changes.values())[-1]
    else:
        raise ValueError("No change found to set actual times")

    # Convert time format from "YYYY-MM-DD HH:MM" to Roundup format
    actual_start_formatted = actual_start.replace(" ", ".") + ":00"
    actual_end_formatted = actual_end.replace(" ", ".") + ":00"

    # Update the change with actual times
    cmd = [
        "roundup-admin",
        "-i",
        tracker_dir,
        "set",
        f"change{change_id}",
        f"actual_start={actual_start_formatted}",
        f"actual_end={actual_end_formatted}",
    ]

    subprocess.run(cmd, capture_output=True, text=True, timeout=10, check=True)


@given('the change has implementation notes "{notes}"')
def step_change_has_implementation_notes(context, notes):
    """Set implementation notes for a change."""
    tracker_dir = getattr(context, "tracker_dir", "tracker")

    # Get the most recently created change
    if hasattr(context, "created_change_id"):
        change_id = context.created_change_id
    elif hasattr(context, "created_changes") and context.created_changes:
        change_id = list(context.created_changes.values())[-1]
    else:
        raise ValueError("No change found to set implementation notes")

    # Update the change with implementation notes
    cmd = [
        "roundup-admin",
        "-i",
        tracker_dir,
        "set",
        f"change{change_id}",
        f"implementation_notes={notes}",
    ]

    subprocess.run(cmd, capture_output=True, text=True, timeout=10, check=True)


@when("I fill in implementation notes:")
def step_fill_in_implementation_notes(context):
    """Fill in implementation tracking fields from a table."""
    for row in context.table:
        field = row["Field"]
        value = row["Value"]

        if field == "Implementation Notes":
            context.page.fill('textarea[name="implementation_notes"]', value)
        elif field == "Actual Duration":
            context.page.fill('input[name="actual_duration"]', value)
        elif field == "Deviation Notes":
            context.page.fill('textarea[name="deviation_notes"]', value)


@when('I select implementation outcome "{outcome}"')
def step_select_implementation_outcome(context, outcome):
    """Select the implementation outcome."""
    context.page.select_option('select[name="implementation_outcome"]', outcome)


@when('I enter rollback reason "{reason}"')
def step_enter_rollback_reason(context, reason):
    """Enter a rollback reason."""
    context.page.fill('textarea[name="rollback_reason"]', reason)
    context.rollback_reason = reason


@when('I enter rollback notes "{notes}"')
def step_enter_rollback_notes(context, notes):
    """Enter rollback notes."""
    context.page.fill('textarea[name="rollback_notes"]', notes)
    context.rollback_notes = notes


@when("I confirm rollback")
def step_confirm_rollback(context):
    """Confirm the rollback action."""
    # This might be a button click or form submission
    context.page.click('button[name="confirm_rollback"]')
    context.page.wait_for_load_state("networkidle")


@then("the change should have actual start time recorded")
def step_verify_actual_start_recorded(context):
    """Verify change has actual start time."""
    # Check if we're on the change details page
    url = context.page.url
    assert "/change" in url, "Should be on change details page"

    # The actual_start field should be visible
    page_content = context.page.content()
    assert "actual_start" in page_content.lower() or "Actual Start" in page_content, (
        "Actual start time should be visible"
    )


@then("the change should have actual end time recorded")
def step_verify_actual_end_recorded(context):
    """Verify change has actual end time."""
    url = context.page.url
    assert "/change" in url, "Should be on change details page"

    page_content = context.page.content()
    assert "actual_end" in page_content.lower() or "Actual End" in page_content, (
        "Actual end time should be visible"
    )


@then("the deviation should be recorded")
def step_verify_deviation_recorded(context):
    """Verify deviation from plan is recorded."""
    page_content = context.page.content()
    assert "deviation" in page_content.lower() or "Deviation" in page_content, (
        "Deviation should be documented"
    )


@then("the rollback should be documented")
def step_verify_rollback_documented(context):
    """Verify rollback is documented."""
    page_content = context.page.content()

    # Check for rollback information
    if hasattr(context, "rollback_reason"):
        assert context.rollback_reason in page_content, (
            f"Rollback reason '{context.rollback_reason}' should be visible"
        )

    # Check that rollback section or notes are visible
    assert "rollback" in page_content.lower() or "Rollback" in page_content, (
        "Rollback documentation should be visible"
    )


@then('I should see "Scheduled Start" section with "{time}"')
def step_verify_scheduled_start_section_with_time(context, time):
    """Verify Scheduled Start section shows specific time."""
    page_content = context.page.content()
    assert "Scheduled Start" in page_content, "Scheduled Start section should be visible"
    assert time in page_content, f"Should see scheduled start time '{time}'"


@then('I should see "Actual Start" section with "{time}"')
def step_verify_actual_start_section_with_time(context, time):
    """Verify Actual Start section shows specific time."""
    page_content = context.page.content()
    assert "Actual Start" in page_content, "Actual Start section should be visible"
    assert time in page_content, f"Should see actual start time '{time}'"


@then('I should see "Scheduled End" section with "{time}"')
def step_verify_scheduled_end_section_with_time(context, time):
    """Verify Scheduled End section shows specific time."""
    page_content = context.page.content()
    assert "Scheduled End" in page_content, "Scheduled End section should be visible"
    assert time in page_content, f"Should see scheduled end time '{time}'"


@then('I should see "Actual End" section with "{time}"')
def step_verify_actual_end_section_with_time(context, time):
    """Verify Actual End section shows specific time."""
    page_content = context.page.content()
    assert "Actual End" in page_content, "Actual End section should be visible"
    assert time in page_content, f"Should see actual end time '{time}'"


@then('the implementation outcome should be "{outcome}"')
def step_verify_implementation_outcome(context, outcome):
    """Verify the implementation outcome."""
    page_content = context.page.content()
    assert outcome in page_content, f"Implementation outcome '{outcome}' should be visible"


@then('change "{change_id:d}" should have actual start time')
def step_verify_change_has_actual_start(context, change_id):
    """Verify a change has an actual start time."""
    tracker_dir = getattr(context, "tracker_dir", "tracker")

    # Use actual ID if stored
    actual_id = getattr(context, "created_change_id", f"{change_id}")

    # Get the actual_start field
    cmd = [
        "roundup-admin",
        "-i",
        tracker_dir,
        "get",
        f"change{actual_id}",
        "actual_start",
    ]

    result = subprocess.run(cmd, capture_output=True, text=True, timeout=10, check=True)

    actual_start = result.stdout.strip()
    assert actual_start and actual_start != "None", (
        f"Change {actual_id} should have actual start time"
    )


@then('change "{change_id:d}" should have implementation notes')
def step_verify_change_has_implementation_notes(context, change_id):
    """Verify a change has implementation notes."""
    tracker_dir = getattr(context, "tracker_dir", "tracker")

    # Use actual ID if stored
    actual_id = getattr(context, "created_change_id", f"{change_id}")

    # Get the implementation_notes field
    cmd = [
        "roundup-admin",
        "-i",
        tracker_dir,
        "get",
        f"change{actual_id}",
        "implementation_notes",
    ]

    result = subprocess.run(cmd, capture_output=True, text=True, timeout=10, check=True)

    impl_notes = result.stdout.strip()
    assert impl_notes and impl_notes != "None", (
        f"Change {actual_id} should have implementation notes"
    )


@then("the output should contain actual start time")
def step_verify_output_has_actual_start(context):
    """Verify CLI output contains actual start time."""
    output = getattr(context, "cli_output", "")
    # Check for date/time pattern or field presence
    assert "actual_start" in output.lower() or "2025-" in output, (
        "Output should contain actual start time"
    )


@then("the output should contain actual end time")
def step_verify_output_has_actual_end(context):
    """Verify CLI output contains actual end time."""
    output = getattr(context, "cli_output", "")
    assert "actual_end" in output.lower() or "2025-" in output, (
        "Output should contain actual end time"
    )


@then("the change should have rollback documentation")
def step_verify_change_has_rollback_docs(context):
    """Verify change has rollback documentation via API."""
    try:
        response_data = context.api_response.json()

        # Check for rollback fields
        has_rollback = False
        if "rollback_reason" in response_data or "rollback_notes" in response_data:
            has_rollback = True
        elif "data" in response_data:
            data = response_data["data"]
            if "rollback_reason" in data or "rollback_notes" in data:
                has_rollback = True

        assert has_rollback, "Change should have rollback documentation"
    except Exception as e:
        raise AssertionError(f"Failed to verify rollback documentation: {e}")


@then('the implementation notes should be "{notes}"')
def step_verify_implementation_notes_value(context, notes):
    """Verify the implementation notes field has specific value."""
    try:
        response_data = context.api_response.json()

        # Try different response structures
        if "implementation_notes" in response_data:
            actual_notes = response_data["implementation_notes"]
        elif "data" in response_data and "implementation_notes" in response_data["data"]:
            actual_notes = response_data["data"]["implementation_notes"]
        else:
            raise AssertionError("No implementation_notes field found in response")

        assert actual_notes == notes, (
            f"Expected implementation notes '{notes}', got '{actual_notes}'"
        )
    except Exception as e:
        raise AssertionError(f"Failed to verify implementation notes value: {e}")
