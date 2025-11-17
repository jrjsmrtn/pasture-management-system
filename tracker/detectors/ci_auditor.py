# SPDX-FileCopyrightText: 2025 Georges Martin <jrjsmrtn@gmail.com>
# SPDX-License-Identifier: MIT

"""Configuration Item auditor for validation."""


def audit_ci_required_fields(db, cl, nodeid, newvalues):
    """Validate required fields for Configuration Items.

    Required fields:
    - name: CI must have a name
    - type: CI must have a type
    - status: CI must have a status
    """
    # For new CIs (nodeid is None), ensure required fields are present
    if nodeid is None:
        # Check name first (most important field)
        name = newvalues.get("name", "").strip()
        if not name:
            raise ValueError("Name is required")

        # Check type is provided
        if "type" not in newvalues or not newvalues.get("type"):
            raise ValueError("Type is required")

        # Check status is provided
        if "status" not in newvalues or not newvalues.get("status"):
            raise ValueError("Status is required")
    else:
        # For updates, only check name if it's being modified
        if "name" in newvalues:
            name = newvalues.get("name", "").strip()
            if not name:
                raise ValueError("Name is required")


def init(db):
    """Register CI auditors."""
    # Fire before changes are made
    db.ci.audit("create", audit_ci_required_fields)
    db.ci.audit("set", audit_ci_required_fields)
