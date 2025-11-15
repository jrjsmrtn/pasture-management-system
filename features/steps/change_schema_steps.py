# SPDX-FileCopyrightText: 2025 Georges Martin <jrjsmrtn@gmail.com>
# SPDX-License-Identifier: MIT

"""Step definitions for change schema verification."""

import requests
from behave import then, when
from requests.auth import HTTPBasicAuth


@when('I GET "{endpoint}" via API')
def step_get_via_api(context, endpoint):
    """Send a GET request to the API."""
    api_url = "http://localhost:8080/pms"
    full_url = f"{api_url}{endpoint}"
    auth = HTTPBasicAuth("admin", "admin")

    response = requests.get(full_url, auth=auth, timeout=30)
    context.api_response = response
    context.api_status_code = response.status_code
    context.api_response_data = response.json() if response.status_code == 200 else response.text


@then('the response should contain collection "{collection_name}"')
def step_response_contains_collection(context, collection_name):
    """Verify the response contains a collection with the given name."""
    response_data = context.api_response.json()
    assert collection_name in response_data, f"Collection '{collection_name}' not found in response. Keys: {response_data.keys()}"
    assert isinstance(response_data[collection_name], dict), f"Collection '{collection_name}' is not a dict"


@then('the response should contain changepriority "{name}"')
def step_response_contains_changepriority(context, name):
    """Verify a changepriority with specific name exists in the response."""
    response_data = context.api_response.json()
    collection = response_data.get("data", {}).get("collection", [])
    auth = HTTPBasicAuth("admin", "admin")

    # Find the changepriority with the given name by fetching each item
    found = False
    for item in collection:
        item_link = item.get("link")
        if item_link:
            detail_response = requests.get(item_link, auth=auth, timeout=30)
            if detail_response.status_code == 200:
                detail_data = detail_response.json()
                if detail_data.get("data", {}).get("attributes", {}).get("name") == name:
                    found = True
                    break

    assert found, f"Changepriority '{name}' not found in response. Collection: {collection}"


@then('the response should contain changecategory "{name}"')
def step_response_contains_changecategory(context, name):
    """Verify a changecategory with specific name exists in the response."""
    response_data = context.api_response.json()
    collection = response_data.get("data", {}).get("collection", [])
    auth = HTTPBasicAuth("admin", "admin")

    # Find the changecategory with the given name by fetching each item
    found = False
    for item in collection:
        item_link = item.get("link")
        if item_link:
            detail_response = requests.get(item_link, auth=auth, timeout=30)
            if detail_response.status_code == 200:
                detail_data = detail_response.json()
                if detail_data.get("data", {}).get("attributes", {}).get("name") == name:
                    found = True
                    break

    assert found, f"Changecategory '{name}' not found in response. Collection: {collection}"


@then('the response should contain changestatus "{name}"')
def step_response_contains_changestatus(context, name):
    """Verify a changestatus with specific name exists in the response."""
    response_data = context.api_response.json()
    collection = response_data.get("data", {}).get("collection", [])
    auth = HTTPBasicAuth("admin", "admin")

    # Find the changestatus with the given name by fetching each item
    found = False
    for item in collection:
        item_link = item.get("link")
        if item_link:
            detail_response = requests.get(item_link, auth=auth, timeout=30)
            if detail_response.status_code == 200:
                detail_data = detail_response.json()
                if detail_data.get("data", {}).get("attributes", {}).get("name") == name:
                    found = True
                    break

    assert found, f"Changestatus '{name}' not found in response. Collection: {collection}"
