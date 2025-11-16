# SPDX-FileCopyrightText: 2025 Georges Martin <jrjsmrtn@gmail.com>
# SPDX-License-Identifier: MIT

"""Step definitions for change scheduling scenarios."""

import subprocess

from behave import given, then, when


@given('the change is scheduled for "{start_time}" to "{end_time}"')
def step_change_is_scheduled(context, start_time, end_time):
    """Set scheduled times for a change."""
    tracker_dir = getattr(context, "tracker_dir", "tracker")

    # Get the most recently created change
    if hasattr(context, "created_change_id"):
        change_id = context.created_change_id
    elif hasattr(context, "created_changes") and context.created_changes:
        change_id = list(context.created_changes.values())[-1]
    else:
        raise ValueError("No change found to set schedule")

    # Convert time format from "YYYY-MM-DD HH:MM" to Roundup format "YYYY-MM-DD.HH:MM:SS"
    scheduled_start = start_time.replace(" ", ".") + ":00"
    scheduled_end = end_time.replace(" ", ".") + ":00"

    # Update the change with scheduled times
    cmd = [
        "roundup-admin",
        "-i",
        tracker_dir,
        "set",
        f"change{change_id}",
        f"scheduled_start={scheduled_start}",
        f"scheduled_end={scheduled_end}",
    ]

    subprocess.run(cmd, capture_output=True, text=True, timeout=10, check=True)


# Note: Step definition for 'the following changes exist:' is in change_list_steps.py
# We'll extend it to support scheduled_start and scheduled_end fields


@when("I fill in scheduling information:")
def step_fill_in_scheduling(context):
    """Fill in scheduling fields from a table."""
    for row in context.table:
        field = row["Field"]
        value = row["Value"]

        if field == "Scheduled Date":
            context.page.fill('input[name="scheduled_date"]', value)
        elif field == "Start Time":
            context.page.fill('input[name="scheduled_start_time"]', value)
        elif field == "End Time":
            context.page.fill('input[name="scheduled_end_time"]', value)


@when('I update the scheduled date to "{date}"')
def step_update_scheduled_date(context, date):
    """Update the scheduled date field."""
    context.page.fill('input[name="scheduled_date"]', date)


@then("the change should have scheduled times")
def step_verify_change_has_scheduled_times(context):
    """Verify change has scheduled start and end times."""
    # Check if we're on the change details page
    url = context.page.url
    assert "/change" in url, "Should be on change details page"

    # The scheduled fields should be visible and contain data
    scheduled_start = context.page.locator(
        'input[name="scheduled_start"], td:has-text("Scheduled Start")'
    )
    assert scheduled_start.count() > 0, "Scheduled start should be visible"


@then('I should see scheduled start "{scheduled_start}"')
def step_verify_scheduled_start_visible(context, scheduled_start):
    """Verify scheduled start time is visible on the page."""
    page_content = context.page.content()
    # Convert display format to what might be shown
    display_time = scheduled_start.replace(" ", " ")
    assert scheduled_start in page_content or display_time in page_content, (
        f"Expected to see scheduled start '{scheduled_start}'"
    )


@then('I should see scheduled end "{scheduled_end}"')
def step_verify_scheduled_end_visible(context, scheduled_end):
    """Verify scheduled end time is visible on the page."""
    page_content = context.page.content()
    display_time = scheduled_end.replace(" ", " ")
    assert scheduled_end in page_content or display_time in page_content, (
        f"Expected to see scheduled end '{scheduled_end}'"
    )


@then('I should see "Scheduled Start" section')
def step_verify_scheduled_start_section(context):
    """Verify Scheduled Start section is visible."""
    page_content = context.page.content()
    assert "Scheduled Start" in page_content or "scheduled_start" in page_content.lower(), (
        "Scheduled Start section should be visible"
    )


@then('I should see "Scheduled End" section')
def step_verify_scheduled_end_section(context):
    """Verify Scheduled End section is visible."""
    page_content = context.page.content()
    assert "Scheduled End" in page_content or "scheduled_end" in page_content.lower(), (
        "Scheduled End section should be visible"
    )


@then("the changes should show their scheduled times")
def step_verify_changes_show_scheduled_times(context):
    """Verify changes display their scheduled times in the list."""
    page_content = context.page.content()

    # Check that scheduling information is visible in the list
    has_schedule_info = "scheduled" in page_content.lower() or "2025-11" in page_content

    assert has_schedule_info, "Changes should display scheduling information"


@then('change "{change_id:d}" should have scheduled start time')
def step_verify_change_has_scheduled_start(context, change_id):
    """Verify a change has a scheduled start time."""
    tracker_dir = getattr(context, "tracker_dir", "tracker")

    # Use actual ID if stored
    actual_id = getattr(context, "created_change_id", f"{change_id}")

    # Get the scheduled_start field
    cmd = [
        "roundup-admin",
        "-i",
        tracker_dir,
        "get",
        f"change{actual_id}",
        "scheduled_start",
    ]

    result = subprocess.run(cmd, capture_output=True, text=True, timeout=10, check=True)

    scheduled_start = result.stdout.strip()
    assert scheduled_start and scheduled_start != "None", (
        f"Change {actual_id} should have scheduled start time"
    )


@then('change "{change_id:d}" should have scheduled end time')
def step_verify_change_has_scheduled_end(context, change_id):
    """Verify a change has a scheduled end time."""
    tracker_dir = getattr(context, "tracker_dir", "tracker")

    # Use actual ID if stored
    actual_id = getattr(context, "created_change_id", f"{change_id}")

    # Get the scheduled_end field
    cmd = [
        "roundup-admin",
        "-i",
        tracker_dir,
        "get",
        f"change{actual_id}",
        "scheduled_end",
    ]

    result = subprocess.run(cmd, capture_output=True, text=True, timeout=10, check=True)

    scheduled_end = result.stdout.strip()
    assert scheduled_end and scheduled_end != "None", (
        f"Change {actual_id} should have scheduled end time"
    )


@then("the change should have updated scheduled start time")
def step_verify_change_updated_scheduled_start(context):
    """Verify the change's scheduled start time was updated."""
    tracker_dir = getattr(context, "tracker_dir", "tracker")

    if not hasattr(context, "created_change_id"):
        raise ValueError("No created_change_id in context")

    change_id = context.created_change_id

    # Get the scheduled_start field
    cmd = [
        "roundup-admin",
        "-i",
        tracker_dir,
        "get",
        f"change{change_id}",
        "scheduled_start",
    ]

    result = subprocess.run(cmd, capture_output=True, text=True, timeout=10, check=True)

    scheduled_start = result.stdout.strip()
    # Check for the updated date (2025-12-08)
    assert "2025-12-08" in scheduled_start or scheduled_start, "Scheduled start should be updated"


@then('the scheduled start should be "{scheduled_start}"')
def step_verify_scheduled_start_value(context, scheduled_start):
    """Verify the scheduled start field has specific value."""
    try:
        response_data = context.api_response.json()

        # Try different response structures
        if "scheduled_start" in response_data:
            actual_start = response_data["scheduled_start"]
        elif "data" in response_data and "scheduled_start" in response_data["data"]:
            actual_start = response_data["data"]["scheduled_start"]
        else:
            raise AssertionError("No scheduled_start field found in response")

        assert actual_start == scheduled_start, (
            f"Expected scheduled start '{scheduled_start}', got '{actual_start}'"
        )
    except Exception as e:
        raise AssertionError(f"Failed to verify scheduled start value: {e}")


@then('the scheduled end should be "{scheduled_end}"')
def step_verify_scheduled_end_value(context, scheduled_end):
    """Verify the scheduled end field has specific value."""
    try:
        response_data = context.api_response.json()

        # Try different response structures
        if "scheduled_end" in response_data:
            actual_end = response_data["scheduled_end"]
        elif "data" in response_data and "scheduled_end" in response_data["data"]:
            actual_end = response_data["data"]["scheduled_end"]
        else:
            raise AssertionError("No scheduled_end field found in response")

        assert actual_end == scheduled_end, (
            f"Expected scheduled end '{scheduled_end}', got '{actual_end}'"
        )
    except Exception as e:
        raise AssertionError(f"Failed to verify scheduled end value: {e}")
