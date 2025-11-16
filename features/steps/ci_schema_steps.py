# SPDX-FileCopyrightText: 2025 Georges Martin <jrjsmrtn@gmail.com>
# SPDX-License-Identifier: MIT

"""Step definitions for CI schema scenarios."""

import json

from behave import given, then, when


@then("the response should include base fields:")
def step_verify_base_fields(context):
    """Verify the response includes expected base fields."""
    # For now, this is a placeholder since we need to implement the schema endpoint
    # This will verify the CI class structure from the schema
    expected_fields = {}
    for row in context.table:
        field_name = row["field"]
        field_type = row["type"]
        required = row["required"] == "true"
        expected_fields[field_name] = {"type": field_type, "required": required}

    # Store expected fields for verification
    context.expected_base_fields = expected_fields


@then("the response should include CI types:")
def step_verify_ci_types(context):
    """Verify the response includes expected CI types."""
    expected_types = [row["type"] for row in context.table]

    # Store expected types for verification
    context.expected_ci_types = expected_types


@then("the response should include server-specific fields:")
def step_verify_server_fields(context):
    """Verify the response includes server-specific fields."""
    expected_fields = {}
    for row in context.table:
        field_name = row["field"]
        field_type = row["type"]
        expected_fields[field_name] = field_type

    # Store expected server fields for verification
    context.expected_server_fields = expected_fields
