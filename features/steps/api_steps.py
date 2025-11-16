# SPDX-FileCopyrightText: 2025 Georges Martin <jrjsmrtn@gmail.com>
# SPDX-License-Identifier: MIT

"""Step definitions for REST API interactions with Roundup tracker."""

import json

import requests
from behave import given, then, when
from requests.auth import HTTPBasicAuth

from features.steps.common import PRIORITY_MAP


@given("the Roundup REST API is accessible")
def step_api_accessible(context):
    """Verify the Roundup REST API is accessible."""
    # Get the API URL from context.tracker_url (configured in environment.py)
    tracker_url = context.tracker_url
    api_url = f"{tracker_url.rstrip('/')}/rest/data"
    context.api_url = api_url

    # Simple connectivity test
    try:
        response = requests.get(f"{api_url}/issue", auth=HTTPBasicAuth("admin", "admin"), timeout=5)
        assert response.status_code in [
            200,
            401,
            403,
        ], f"API not accessible. Status: {response.status_code}"
    except requests.RequestException as e:
        raise AssertionError(f"API not accessible: {e}")


@given("I have a valid API credential")
def step_valid_api_credential(context):
    """Set up valid API credentials."""
    # Use admin credentials for testing
    context.api_auth = HTTPBasicAuth("admin", "admin")
    context.api_authenticated = True


@when("I POST to the API with:")
def step_post_to_api(context):
    """POST data to the REST API to create an issue."""
    # Build the request payload
    payload = {}
    issue_data = {}

    for row in context.table:
        field_name = row["field"]
        field_value = row["value"]

        if field_name == "title":
            payload["title"] = field_value
            issue_data["title"] = field_value
        elif field_name == "priority":
            # Map priority label to ID
            priority_id = PRIORITY_MAP.get(field_value.lower())
            if priority_id:
                payload["priority"] = priority_id
                issue_data["priority"] = field_value
        else:
            # For other fields, pass as-is
            payload[field_name] = field_value
            issue_data[field_name] = field_value

    # Store issue data for later verification
    context.api_issue_data = issue_data

    # Prepare headers with CSRF protection headers
    # Extract base URL (protocol://host:port) from tracker_url
    from urllib.parse import urlparse

    parsed = urlparse(context.tracker_url)
    base_url = f"{parsed.scheme}://{parsed.netloc}"

    headers = {
        "Content-Type": "application/json",
        "X-Requested-With": "XMLHttpRequest",
        "Origin": base_url,
        "Referer": context.tracker_url,
    }

    # Make the POST request
    auth = getattr(context, "api_auth", None)
    response = requests.post(
        f"{context.api_url}/issue", json=payload, headers=headers, auth=auth, timeout=30
    )

    # Store the response
    context.api_response = response
    context.api_status_code = response.status_code

    # Try to parse JSON response
    try:
        context.api_response_data = response.json()
    except json.JSONDecodeError:
        context.api_response_data = None


@when("I POST to the API without authentication with:")
def step_post_without_auth(context):
    """POST data to the REST API without authentication."""
    # Build the request payload
    payload = {}

    for row in context.table:
        field_name = row["field"]
        field_value = row["value"]
        payload[field_name] = field_value

    # Prepare headers
    # Extract base URL (protocol://host:port) from tracker_url
    from urllib.parse import urlparse

    parsed = urlparse(context.tracker_url)
    base_url = f"{parsed.scheme}://{parsed.netloc}"

    headers = {
        "Content-Type": "application/json",
        "X-Requested-With": "XMLHttpRequest",
        "Origin": base_url,
        "Referer": context.tracker_url,
    }

    # Make the POST request WITHOUT auth
    response = requests.post(
        f"{context.api_url}/issue",
        json=payload,
        headers=headers,
        auth=None,  # No authentication
        timeout=30,
    )

    # Store the response
    context.api_response = response
    context.api_status_code = response.status_code


@then("the API response status should be {expected_status}")
def step_verify_api_status(context, expected_status):
    """Verify the API response status code."""
    # Handle "201 or 200" format
    if " or " in expected_status:
        allowed_statuses = [int(s.strip()) for s in expected_status.split(" or ")]
        assert context.api_status_code in allowed_statuses, (
            f"Expected status {expected_status}, got {context.api_status_code}. Response: {context.api_response.text}"
        )
    else:
        expected_code = int(expected_status)
        assert context.api_status_code == expected_code, (
            f"Expected status {expected_code}, got {context.api_status_code}. Response: {context.api_response.text}"
        )


@then("the response should contain an issue ID")
def step_response_contains_issue_id(context):
    """Verify the response contains an issue ID."""
    assert context.api_response_data is not None, "Response is not valid JSON"

    # Roundup REST API returns: {"data": {"id": "14", "link": "..."}}
    data = context.api_response_data.get("data", {})
    issue_id = data.get("id")

    assert issue_id is not None, f"No issue ID in response: {context.api_response_data}"
    assert issue_id.isdigit(), f"Issue ID is not numeric: {issue_id}"

    # Store for later verification
    context.created_issue_id = f"issue{issue_id}"
    context.api_issue_id = issue_id


@then("the issue should not be created via API")
def step_issue_not_created_via_api(context):
    """Verify the issue was not created (for negative tests)."""
    # Just verify the status code was not successful
    assert context.api_status_code not in [
        200,
        201,
    ], f"Issue should not have been created, but got status {context.api_status_code}"
