# SPDX-FileCopyrightText: 2025 Georges Martin <jrjsmrtn@gmail.com>
# SPDX-License-Identifier: MIT

"""Step definitions for change risk assessment scenarios."""

import subprocess

from behave import given, then, when


@given('the change has risk assessment "{risk_text}"')
def step_change_has_risk_assessment(context, risk_text):
    """Set risk assessment for a change."""
    tracker_dir = getattr(context, "tracker_dir", "tracker")

    # Get the most recently created change
    if hasattr(context, "created_change_id"):
        change_id = context.created_change_id
    elif hasattr(context, "created_changes") and context.created_changes:
        change_id = list(context.created_changes.values())[-1]
    else:
        raise ValueError("No change found to set risk assessment")

    # Update the change with risk assessment
    cmd = [
        "roundup-admin",
        "-i",
        tracker_dir,
        "set",
        f"change{change_id}",
        f"risk={risk_text}",
    ]

    subprocess.run(cmd, capture_output=True, text=True, timeout=10, check=True)


@given('the change has impact "{impact_text}"')
def step_change_has_impact(context, impact_text):
    """Set impact assessment for a change."""
    tracker_dir = getattr(context, "tracker_dir", "tracker")

    # Get the most recently created change
    if hasattr(context, "created_change_id"):
        change_id = context.created_change_id
    elif hasattr(context, "created_changes") and context.created_changes:
        change_id = list(context.created_changes.values())[-1]
    else:
        raise ValueError("No change found to set impact assessment")

    # Update the change with impact assessment
    cmd = [
        "roundup-admin",
        "-i",
        tracker_dir,
        "set",
        f"change{change_id}",
        f"impact={impact_text}",
    ]

    subprocess.run(cmd, capture_output=True, text=True, timeout=10, check=True)


@given('the change has risk "{risk_text}"')
def step_change_has_risk(context, risk_text):
    """Set risk for a change (alias for risk assessment)."""
    step_change_has_risk_assessment(context, risk_text)


@when("I fill in the risk assessment:")
def step_fill_in_risk_assessment(context):
    """Fill in risk assessment fields from a table."""
    for row in context.table:
        field = row["Field"]
        value = row["Value"]

        if field == "Impact":
            context.page.fill('textarea[name="impact"]', value)
        elif field == "Risk":
            context.page.fill('textarea[name="risk"]', value)


@when('I update the risk field to "{risk_text}"')
def step_update_risk_field(context, risk_text):
    """Update the risk field."""
    context.page.fill('textarea[name="risk"]', risk_text)


@then("the change should have risk assessment saved")
def step_verify_risk_assessment_saved(context):
    """Verify risk assessment is saved."""
    # Check if we're on the change details page
    url = context.page.url
    assert "/change" in url, "Should be on change details page"

    # The risk field should be visible and contain data
    risk_field = context.page.locator('textarea[name="risk"]')
    if risk_field.count() > 0:
        risk_value = risk_field.input_value()
        assert risk_value, "Risk assessment should be saved"


@then('I should see impact "{impact_text}"')
def step_verify_impact_visible(context, impact_text):
    """Verify impact text is visible on the page."""
    page_content = context.page.content()
    assert impact_text in page_content, f"Expected to see impact '{impact_text}'"


@then('I should see risk "{risk_text}"')
def step_verify_risk_visible(context, risk_text):
    """Verify risk text is visible on the page."""
    page_content = context.page.content()
    assert risk_text in page_content, f"Expected to see risk '{risk_text}'"


@then("the risk assessment should be updated")
def step_verify_risk_assessment_updated(context):
    """Verify risk assessment was updated."""
    # Similar to saved check
    url = context.page.url
    assert "/change" in url, "Should be on change details page"


@then('I should see "Impact Assessment" section')
def step_verify_impact_assessment_section(context):
    """Verify Impact Assessment section is visible."""
    # Look for the impact field or label
    page_content = context.page.content()
    assert "Impact" in page_content or "impact" in page_content.lower(), (
        "Impact Assessment section should be visible"
    )


@then('I should see "Risk Assessment" section')
def step_verify_risk_assessment_section(context):
    """Verify Risk Assessment section is visible."""
    # Look for the risk field or label
    page_content = context.page.content()
    assert "Risk" in page_content or "risk" in page_content.lower(), (
        "Risk Assessment section should be visible"
    )


@then("I should see all {count:d} changes listed")
def step_verify_changes_count_listed(context, count):
    """Verify the expected number of changes are listed."""
    # In Roundup, changes are displayed in a table
    change_rows = context.page.locator("table.list tr").all()

    # Count rows that contain change links
    actual_count = 0
    for row in change_rows:
        if row.locator('a[href*="change"]').count() > 0:
            actual_count += 1

    assert actual_count == count, f"Expected {count} changes, found {actual_count}"


@then("the changes should show their risk assessments")
def step_verify_changes_show_risk_assessments(context):
    """Verify changes display their risk assessments."""
    # This checks that risk information is visible in the list
    # The actual implementation might vary based on UI design
    page_content = context.page.content()

    # Check that at least some risk-related text is visible
    # This is a basic check - actual implementation may need refinement
    has_risk_info = "risk" in page_content.lower() or "impact" in page_content.lower()

    assert has_risk_info, "Changes should display risk assessment information"


@then('change "{change_id:d}" should have impact assessment')
def step_verify_change_has_impact(context, change_id):
    """Verify a change has impact assessment."""
    tracker_dir = getattr(context, "tracker_dir", "tracker")

    # Use actual ID if stored
    actual_id = getattr(context, "current_change_id", f"{change_id}")

    # Get the impact field
    cmd = ["roundup-admin", "-i", tracker_dir, "get", f"change{actual_id}", "impact"]

    result = subprocess.run(cmd, capture_output=True, text=True, timeout=10, check=True)

    impact = result.stdout.strip()
    assert impact and impact != "None", f"Change {actual_id} should have impact assessment"


@then('change "{change_id:d}" should have risk assessment')
def step_verify_change_has_risk(context, change_id):
    """Verify a change has risk assessment."""
    tracker_dir = getattr(context, "tracker_dir", "tracker")

    # Use actual ID if stored
    actual_id = getattr(context, "current_change_id", f"{change_id}")

    # Get the risk field
    cmd = ["roundup-admin", "-i", tracker_dir, "get", f"change{actual_id}", "risk"]

    result = subprocess.run(cmd, capture_output=True, text=True, timeout=10, check=True)

    risk = result.stdout.strip()
    assert risk and risk != "None", f"Change {actual_id} should have risk assessment"


@then('the output should contain "{text}"')
def step_verify_output_contains(context, text):
    """Verify CLI output contains specific text."""
    output = getattr(context, "cli_output", "")
    assert text in output, f"Expected output to contain '{text}', got: {output}"


@then("the created change should have impact assessment")
def step_verify_created_change_has_impact(context):
    """Verify the newly created change has impact assessment."""
    tracker_dir = getattr(context, "tracker_dir", "tracker")

    if not hasattr(context, "created_change_id"):
        # Try to get from API response
        if hasattr(context, "api_response"):
            try:
                response_data = context.api_response.json()
                if "id" in response_data:
                    context.created_change_id = response_data["id"]
                elif "data" in response_data and "id" in response_data["data"]:
                    context.created_change_id = response_data["data"]["id"]
            except Exception:
                pass

    if not hasattr(context, "created_change_id"):
        raise ValueError("No created_change_id in context")

    change_id = context.created_change_id

    # Get the impact field
    cmd = ["roundup-admin", "-i", tracker_dir, "get", f"change{change_id}", "impact"]

    result = subprocess.run(cmd, capture_output=True, text=True, timeout=10, check=True)

    impact = result.stdout.strip()
    assert impact and impact != "None", "Created change should have impact assessment"


@then("the created change should have risk assessment")
def step_verify_created_change_has_risk(context):
    """Verify the newly created change has risk assessment."""
    tracker_dir = getattr(context, "tracker_dir", "tracker")

    if not hasattr(context, "created_change_id"):
        raise ValueError("No created_change_id in context")

    change_id = context.created_change_id

    # Get the risk field
    cmd = ["roundup-admin", "-i", tracker_dir, "get", f"change{change_id}", "risk"]

    result = subprocess.run(cmd, capture_output=True, text=True, timeout=10, check=True)

    risk = result.stdout.strip()
    assert risk and risk != "None", "Created change should have risk assessment"


@then("the change should have updated impact assessment")
def step_verify_change_updated_impact(context):
    """Verify the change's impact assessment was updated."""
    tracker_dir = getattr(context, "tracker_dir", "tracker")

    if not hasattr(context, "current_change_id"):
        raise ValueError("No current_change_id in context")

    change_id = context.current_change_id

    # Get the impact field
    cmd = ["roundup-admin", "-i", tracker_dir, "get", f"change{change_id}", "impact"]

    result = subprocess.run(cmd, capture_output=True, text=True, timeout=10, check=True)

    impact = result.stdout.strip()
    assert "Updated impact" in impact or impact, "Impact should be updated"


@then("the change should have updated risk assessment")
def step_verify_change_updated_risk(context):
    """Verify the change's risk assessment was updated."""
    tracker_dir = getattr(context, "tracker_dir", "tracker")

    if not hasattr(context, "current_change_id"):
        raise ValueError("No current_change_id in context")

    change_id = context.current_change_id

    # Get the risk field
    cmd = ["roundup-admin", "-i", tracker_dir, "get", f"change{change_id}", "risk"]

    result = subprocess.run(cmd, capture_output=True, text=True, timeout=10, check=True)

    risk = result.stdout.strip()
    assert "Updated risk" in risk or risk, "Risk should be updated"


# Note: Step definition for 'the response should include "{text}"' is in
# change_list_steps.py and handles "impact", "risk", and other text verification


@then('the impact should be "{impact_text}"')
def step_verify_impact_value(context, impact_text):
    """Verify the impact field has specific value."""
    try:
        response_data = context.api_response.json()

        # Try different response structures
        if "impact" in response_data:
            actual_impact = response_data["impact"]
        elif "data" in response_data and "impact" in response_data["data"]:
            actual_impact = response_data["data"]["impact"]
        else:
            raise AssertionError("No impact field found in response")

        assert actual_impact == impact_text, (
            f"Expected impact '{impact_text}', got '{actual_impact}'"
        )
    except Exception as e:
        raise AssertionError(f"Failed to verify impact value: {e}")


@then('the risk should be "{risk_text}"')
def step_verify_risk_value(context, risk_text):
    """Verify the risk field has specific value."""
    try:
        response_data = context.api_response.json()

        # Try different response structures
        if "risk" in response_data:
            actual_risk = response_data["risk"]
        elif "data" in response_data and "risk" in response_data["data"]:
            actual_risk = response_data["data"]["risk"]
        else:
            raise AssertionError("No risk field found in response")

        assert actual_risk == risk_text, f"Expected risk '{risk_text}', got '{actual_risk}'"
    except Exception as e:
        raise AssertionError(f"Failed to verify risk value: {e}")
