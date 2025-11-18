# SPDX-FileCopyrightText: 2025 Georges Martin <jrjsmrtn@gmail.com>
# SPDX-License-Identifier: MIT

"""Step definitions for CI search and filtering scenarios."""

import re
import subprocess

from behave import given, then, when


@given("the following CIs exist:")
def step_create_multiple_cis(context):
    """Create multiple CIs from a table."""
    if not hasattr(context, "ci_map"):
        context.ci_map = {}

    # Type mapping
    type_mapping = {
        "Server": "1",
        "Network Device": "2",
        "Storage": "3",
        "Software": "4",
        "Service": "5",
        "Virtual Machine": "6",
    }

    # Status mapping
    status_mapping = {
        "Planning": "1",
        "Ordered": "2",
        "In Stock": "3",
        "Deployed": "4",
        "Active": "5",
        "Maintenance": "6",
        "Retired": "7",
    }

    # Criticality mapping
    criticality_mapping = {
        "Very Low": "1",
        "Low": "2",
        "Medium": "3",
        "High": "4",
        "Very High": "5",
    }

    for row in context.table:
        name = row["name"]
        ci_type = row["type"]
        type_id = type_mapping.get(ci_type, ci_type)

        # Build command args
        cmd = [
            "roundup-admin",
            "-i",
            "tracker",
            "create",
            "ci",
            f"name={name}",
            f"type={type_id}",
        ]

        # Add status field (required by auditor, default to "Active" if not specified)
        if "status" in row.headings:
            status = row.get("status")
            if status:
                status_id = status_mapping.get(status, status)
                cmd.append(f"status={status_id}")
        else:
            # Default to "Active" status (ID 5)
            cmd.append("status=5")

        if "criticality" in row.headings:
            criticality = row.get("criticality")
            if criticality:
                crit_id = criticality_mapping.get(criticality, criticality)
                cmd.append(f"criticality={crit_id}")

        if "location" in row.headings:
            location = row.get("location")
            if location:
                cmd.append(f"location={location}")

        # Create the CI
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        assert result.returncode == 0, f"Failed to create CI: {result.stderr}"

        # Store CI ID
        ci_id = result.stdout.strip()
        context.ci_map[name] = ci_id


@when('I search for "{search_term}"')
def step_search_for_term(context, search_term):
    """Enter search term in the search box."""
    # Find and fill the search input
    context.page.fill('input[name="@search_text"]', search_term)
    # Submit the search form or click search button
    context.page.click('input[type="submit"][value="Search"]')
    context.page.wait_for_load_state("networkidle")


@when('I filter by type "{ci_type}"')
def step_filter_by_type(context, ci_type):
    """Filter CIs by type."""
    # Type mapping
    type_mapping = {
        "Server": "1",
        "Network Device": "2",
        "Storage": "3",
        "Software": "4",
        "Service": "5",
        "Virtual Machine": "6",
    }
    type_id = type_mapping.get(ci_type, ci_type)

    # Select the type filter
    context.page.select_option('select[name="type"]', type_id)
    # Wait for page load after auto-submit
    context.page.wait_for_load_state("networkidle")


@when('I filter by criticality "{criticality}"')
def step_filter_by_criticality(context, criticality):
    """Filter CIs by criticality level."""
    criticality_mapping = {
        "Very Low": "1",
        "Low": "2",
        "Medium": "3",
        "High": "4",
        "Very High": "5",
    }
    crit_id = criticality_mapping.get(criticality, criticality)

    context.page.select_option('select[name="criticality"]', crit_id)
    context.page.wait_for_load_state("networkidle")


@when('I filter CIs by status "{status}"')
def step_filter_cis_by_status(context, status):
    """Filter CIs by status."""
    status_mapping = {
        "Planning": "1",
        "Ordered": "2",
        "In Stock": "3",
        "Deployed": "4",
        "Active": "5",
        "Maintenance": "6",
        "Retired": "7",
    }
    status_id = status_mapping.get(status, status)

    context.page.select_option('select[name="status"]', status_id)
    context.page.wait_for_load_state("networkidle")


@when('I click quick filter "{filter_name}"')
def step_click_quick_filter(context, filter_name):
    """Click a quick filter button."""
    # Quick filters are typically links or buttons with specific classes/IDs
    context.page.click(f'text="{filter_name}"')
    context.page.wait_for_load_state("networkidle")


@when('I sort by "{column}" ascending')
@when('I sort by "{column}" descending')
def step_sort_by_column(context, column):
    """Sort the CI list by a specific column."""
    # Determine if ascending or descending from the step text
    ascending = "ascending" in context.step.name

    # Click the column header to sort
    # First click sets ascending, second click sets descending
    context.page.click(f'th:has-text("{column}")')
    context.page.wait_for_timeout(500)

    # If we want descending and it's now ascending, click again
    if not ascending:
        context.page.click(f'th:has-text("{column}")')
        context.page.wait_for_timeout(500)


@when('I click "Clear Filters"')
def step_clear_filters(context):
    """Clear all active filters."""
    context.page.click('text="Clear Filters"')
    context.page.wait_for_load_state("networkidle")


@when('I click "Export to CSV"')
def step_export_to_csv(context):
    """Click the Export to CSV button."""
    # Set up download listener before clicking
    with context.page.expect_download() as download_info:
        context.page.click('text="Export to CSV"')
    context.download = download_info.value


@then("I should see {count:d} CIs in the results")
@then("I should see {count:d} CI in the results")
def step_verify_ci_count(context, count):
    """Verify the number of CIs displayed in results."""
    # Look for CI links in the content - each CI has a link like ci1, ci2, etc.
    # This is more reliable than counting table rows
    ci_links = context.page.locator('a[href*="ci"]').filter(has_text=re.compile(r".*"))

    # Filter out navigation links - only count CI item links
    ci_item_links = []
    for i in range(ci_links.count()):
        link = ci_links.nth(i)
        href = link.get_attribute("href")
        # CI item links are like 'ci1', 'ci2', etc. (just ci + number)
        if href and re.match(r"^ci\d+$", href):
            ci_item_links.append(link)

    actual_count = len(ci_item_links)
    assert actual_count == count, f"Expected {count} CIs in results, but found {actual_count}"


@then('I should see CI "{ci_name}"')
def step_verify_ci_visible(context, ci_name):
    """Verify a specific CI is visible in the results."""
    content = context.page.content()
    assert ci_name in content, f"CI '{ci_name}' not found in results"


@then('I should not see CI "{ci_name}"')
def step_verify_ci_not_visible(context, ci_name):
    """Verify a specific CI is NOT visible in the results."""
    content = context.page.content()
    assert ci_name not in content, f"CI '{ci_name}' should not be in results"


@then("the CIs should be displayed in order:")
def step_verify_ci_order(context):
    """Verify CIs are displayed in the specified order."""
    expected_order = [row[0] for row in context.table]

    # Get the actual order from the page
    ci_names = context.page.locator("table.list tbody tr td:first-child").all_text_contents()

    # Extract just the CI names (removing any extra whitespace)
    ci_names = [name.strip() for name in ci_names if name.strip()]

    assert ci_names == expected_order, f"Expected order {expected_order}, but got {ci_names}"


@then("a CSV file should be downloaded")
def step_verify_csv_downloaded(context):
    """Verify a CSV file was downloaded."""
    download = context.download
    assert download is not None, "No file was downloaded"
    assert download.suggested_filename.endswith(".csv"), "Downloaded file is not a CSV"
    # Store download path for further verification
    context.csv_path = download.path()


@then('the CSV should contain "{text}"')
def step_verify_csv_contains(context, text):
    """Verify the CSV file contains specific text."""
    csv_path = context.csv_path
    with open(csv_path, encoding="utf-8") as f:
        csv_content = f.read()
    assert text in csv_content, f"CSV does not contain '{text}'"


@then("the response should be valid JSON")
def step_verify_valid_json(context):
    """Verify the API response is valid JSON."""
    import json

    try:
        json.loads(context.api_response_body)
    except json.JSONDecodeError:
        raise AssertionError("Response is not valid JSON")


@then('the response should include CI "{ci_name}"')
def step_verify_api_includes_ci(context, ci_name):
    """Verify the API response includes a specific CI."""
    import json

    data = json.loads(context.api_response_body)
    # Assuming response is a list of CIs or has a 'cis' field
    ci_names = [ci.get("name") for ci in (data if isinstance(data, list) else data.get("cis", []))]
    assert ci_name in ci_names, f"CI '{ci_name}' not found in API response"
