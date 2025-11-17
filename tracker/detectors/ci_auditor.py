# SPDX-FileCopyrightText: 2025 Georges Martin <jrjsmrtn@gmail.com>
# SPDX-License-Identifier: MIT

"""Configuration Item auditor for validation."""

import logging

from roundup.exceptions import Reject

logger = logging.getLogger(__name__)


def audit_ci_required_fields(db, cl, nodeid, newvalues):
    """Validate required fields for Configuration Items.

    Required fields:
    - name: CI must have a name
    - type: CI must have a type
    - status: CI must have a status
    """
    action = "create" if nodeid is None else "update"
    logger.debug(
        "Auditing CI required fields",
        extra={"nodeid": nodeid, "action": action, "fields": list(newvalues.keys())},
    )

    # For new CIs (nodeid is None), ensure required fields are present
    if nodeid is None:
        # Check name first (most important field)
        name = newvalues.get("name", "") or ""
        name = name.strip() if name else ""
        if not name:
            logger.warning("CI creation rejected: name is required")
            raise Reject("Name is required")

        # Check type is provided
        if "type" not in newvalues or not newvalues.get("type"):
            logger.warning("CI creation rejected: type is required")
            raise Reject("Type is required")

        # Check status is provided
        if "status" not in newvalues or not newvalues.get("status"):
            logger.warning("CI creation rejected: status is required")
            raise Reject("Status is required")

        logger.debug("CI creation validation passed", extra={"name": name})
    else:
        # For updates, only check name if it's being modified
        if "name" in newvalues:
            name = newvalues.get("name", "") or ""
            name = name.strip() if name else ""
            if not name:
                logger.warning("CI update rejected: name is required", extra={"nodeid": nodeid})
                raise Reject("Name is required")

        logger.debug("CI update validation passed", extra={"nodeid": nodeid})


def init(db):
    """Register CI auditors."""
    # Fire before changes are made
    db.ci.audit("create", audit_ci_required_fields)
    db.ci.audit("set", audit_ci_required_fields)
