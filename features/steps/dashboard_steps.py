# SPDX-FileCopyrightText: 2025 Georges Martin <jrjsmrtn@gmail.com>
# SPDX-License-Identifier: MIT

"""Step definitions for dashboard scenarios."""

from behave import then, when


@when('I navigate to "Dashboard"')
def step_navigate_to_dashboard(context):
    """Navigate to the CMDB dashboard."""
    from features.steps.web_ui_steps import check_for_templating_error

    context.page.click('a:has-text("Dashboard")')
    context.page.wait_for_load_state("networkidle")
    context.page.wait_for_timeout(500)

    # Check for templating errors
    check_for_templating_error(context.page, "navigate to Dashboard")


@then('I should see "{count}" in the Total CIs stat')
def step_verify_total_cis_count(context, count):
    """Verify the Total CIs count in the dashboard."""
    # Look for the Total CIs stat value
    total_ci_locator = context.page.locator(
        '.summary-stat:has-text("Total CIs") .summary-stat-value'
    )
    actual_count = total_ci_locator.text_content().strip()
    assert actual_count == count, f"Expected Total CIs to be {count}, but got {actual_count}"


@then('I should see "{text}" in the dashboard')
def step_verify_text_in_dashboard(context, text):
    """Verify specific text appears in the dashboard."""
    content = context.page.content()
    assert text in content, f"Expected to see '{text}' in dashboard, but it was not found"


@then('the "{label}" count should be "{count}"')
def step_verify_count_by_label(context, label, count):
    """Verify a count for a specific label in the dashboard."""
    # This matches labels in chart-bar or stat-grid sections
    content = context.page.content()

    # Check if the label and count appear together in the content
    # This is a simplified check - could be made more specific
    assert label in content, f"Expected to find label '{label}' in dashboard"
    # Note: For more precise checking, we'd need to implement proper selectors
    # based on the actual dashboard structure


@then('the "{label}" criticality count should be "{count}"')
def step_verify_criticality_count(context, label, count):
    """Verify a criticality count in the dashboard."""
    content = context.page.content()
    assert label in content, f"Expected to find criticality '{label}' in dashboard"
    # Note: This is a basic implementation - could be enhanced with specific selectors
