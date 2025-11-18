# SPDX-FileCopyrightText: 2025 Georges Martin <jrjsmrtn@gmail.com>
# SPDX-License-Identifier: MIT

"""Step definitions for CI creation scenarios."""

import json
import subprocess

import requests
from behave import given, then, when
from requests.auth import HTTPBasicAuth

from features.steps.web_ui_steps import check_for_templating_error


@when('I navigate to "CMDB"')
def step_navigate_to_cmdb(context):
    """Navigate to the CMDB page."""
    # Click the CMDB link to preserve session (don't use goto which loses cookies!)
    # Wait for the link to be visible and clickable
    cmdb_link = context.page.locator('a:has-text("View Configuration Items")')
    cmdb_link.wait_for(state="visible", timeout=5000)

    # Use click with navigation wait
    with context.page.expect_navigation():
        cmdb_link.click()

    context.page.wait_for_load_state("networkidle")
    # Additional wait for TAL rendering (Roundup-specific timing)
    context.page.wait_for_timeout(500)

    # Check for templating errors
    check_for_templating_error(context.page, "navigate to CMDB")


@when('I select type "{ci_type}"')
def step_select_ci_type(context, ci_type):
    """Select CI type from dropdown."""
    # Map type names to IDs
    type_mapping = {
        "Server": "1",
        "Network Device": "2",
        "Storage": "3",
        "Software": "4",
        "Service": "5",
        "Virtual Machine": "6",
    }
    type_id = type_mapping.get(ci_type, ci_type)
    context.page.select_option("select[name='type']", type_id)


@when('I select status "{ci_status}"')
def step_select_ci_status(context, ci_status):
    """Select CI status from dropdown."""
    # Map status names to IDs
    status_mapping = {
        "Planning": "1",
        "Ordered": "2",
        "In Stock": "3",
        "Deployed": "4",
        "Active": "5",
        "Maintenance": "6",
        "Retired": "7",
    }
    status_id = status_mapping.get(ci_status, ci_status)
    context.page.select_option("select[name='status']", status_id)


@when('I select criticality "{criticality}"')
def step_select_ci_criticality(context, criticality):
    """Select CI criticality from dropdown."""
    # Map criticality names to IDs
    criticality_mapping = {
        "Very Low": "1",
        "Low": "2",
        "Medium": "3",
        "High": "4",
        "Very High": "5",
    }
    criticality_id = criticality_mapping.get(criticality, criticality)
    context.page.select_option("select[name='criticality']", criticality_id)


@when('I enter name "{name}"')
def step_enter_ci_name(context, name):
    """Enter CI name."""
    context.page.fill("input[name='name']", name)
    # Store the CI name for later verification
    context.ci_name = name


@when('I enter location "{location}"')
def step_enter_location(context, location):
    """Enter CI location."""
    context.page.fill("input[name='location']", location)


@when('I enter CPU cores "{cores}"')
def step_enter_cpu_cores(context, cores):
    """Enter CPU cores."""
    context.page.fill("input[name='cpu_cores']", cores)


@when('I enter RAM GB "{ram}"')
def step_enter_ram_gb(context, ram):
    """Enter RAM in GB."""
    context.page.fill("input[name='ram_gb']", ram)


@when('I enter OS "{os}"')
def step_enter_os(context, os):
    """Enter operating system."""
    context.page.fill("input[name='os']", os)


@when('I enter IP address "{ip}"')
def step_enter_ip_address(context, ip):
    """Enter IP address."""
    context.page.fill("input[name='ip_address']", ip)


@when('I enter ports "{ports}"')
def step_enter_ports(context, ports):
    """Enter number of ports."""
    context.page.fill("input[name='ports']", ports)


@when('I enter capacity GB "{capacity}"')
def step_enter_capacity_gb(context, capacity):
    """Enter storage capacity in GB."""
    context.page.fill("input[name='capacity_gb']", capacity)


@then("the CI should appear in the CMDB")
def step_verify_ci_in_list(context):
    """Verify CI appears in the CMDB list."""
    # Click the "View Configuration Items" link to navigate to CI list
    # (using goto loses session in some cases)
    context.page.click('a:has-text("View Configuration Items")')
    context.page.wait_for_load_state("networkidle")

    # Check for CI name in the list
    ci_name = getattr(context, "ci_name", None)
    assert ci_name, "CI name not set in context"

    content = context.page.content()
    assert ci_name in content, f"CI '{ci_name}' not found in CMDB list"


@then('the CI "{name}" should exist')
def step_verify_ci_exists(context, name):
    """Verify a CI with given name exists."""
    # Click the "View Configuration Items" link to navigate to CI list
    context.page.click('a:has-text("View Configuration Items")')
    context.page.wait_for_load_state("networkidle")

    content = context.page.content()
    assert name in content, f"CI '{name}' not found in CMDB"


@then("the CI should exist in the database")
def step_verify_ci_in_database(context):
    """Verify CI was created in the database via API."""
    # The CI ID should be in the API response
    assert hasattr(context, "api_response_data"), "No API response data found"
    assert context.api_status_code == 201, f"Expected 201, got {context.api_status_code}"


@when('I POST to "{endpoint}" with JSON')
def step_post_json_to_endpoint(context, endpoint):
    """POST JSON data to an API endpoint."""
    # Parse the JSON from the scenario text
    json_data = json.loads(context.text)

    # Get auth from context
    auth = getattr(context, "api_auth", HTTPBasicAuth("admin", "admin"))

    # Make the request
    base_url = context.tracker_url
    # Convert endpoint from /api/cmdb/ci to /rest/data/ci
    if endpoint.startswith("/api/cmdb/"):
        endpoint = endpoint.replace("/api/cmdb/", "/rest/data/")
    elif endpoint.startswith("/api/"):
        endpoint = endpoint.replace("/api/", "/rest/data/")

    url = f"{base_url}{endpoint}"

    headers = {
        "Content-Type": "application/json",
        "X-Requested-With": "rest",
    }

    response = requests.post(url, json=json_data, auth=auth, headers=headers)

    # Store response in context
    context.api_response = response
    context.api_status_code = response.status_code

    if response.status_code in [200, 201]:
        try:
            context.api_response_data = response.json()
        except json.JSONDecodeError:
            context.api_response_data = response.text
    else:
        context.api_response_data = response.text
