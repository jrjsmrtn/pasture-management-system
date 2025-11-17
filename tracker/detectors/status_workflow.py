# SPDX-FileCopyrightText: 2025 Georges Martin <jrjsmrtn@gmail.com>
# SPDX-License-Identifier: MIT

"""
Status workflow detector for enforcing valid issue status transitions.

This detector implements ITIL-inspired workflow rules:
- new → in-progress
- in-progress → resolved
- resolved → closed
- resolved → in-progress (reopening)

Invalid transitions (e.g., new → closed) are rejected.
"""

import logging

from roundup.exceptions import Reject

logger = logging.getLogger(__name__)


def check_status_transition(db, cl, nodeid, newvalues):
    """
    Enforce valid status transitions for issues.

    Args:
        db: Database instance
        cl: Issue class
        nodeid: Issue node ID (None for create)
        newvalues: Dictionary of new values being set

    Raises:
        Reject: If the status transition is invalid
    """
    # Only validate on updates (not creation)
    if nodeid is None:
        return

    # Only validate if status is being changed
    if "status" not in newvalues:
        return

    # Get current and new status
    current_status_id = cl.get(nodeid, "status")
    new_status_id = newvalues["status"]

    # If status hasn't changed, allow it
    if current_status_id == new_status_id:
        return

    # Look up status IDs by name (robust approach - survives database reinitializations)
    status_class = db.getclass("status")
    new_id = status_class.lookup("new")
    in_progress_id = status_class.lookup("in-progress")
    resolved_id = status_class.lookup("resolved")
    closed_id = status_class.lookup("closed")

    # Define valid transitions using looked-up IDs
    VALID_TRANSITIONS = {
        new_id: [in_progress_id],  # new → in-progress
        in_progress_id: [resolved_id],  # in-progress → resolved
        resolved_id: [in_progress_id, closed_id],  # resolved → in-progress (reopen) or closed
        closed_id: [],  # closed is terminal (no transitions allowed)
    }

    # Check if transition is valid
    allowed_statuses = VALID_TRANSITIONS.get(current_status_id, [])

    # Get status names for logging
    current_status_name = status_class.get(current_status_id, "name")
    new_status_name = status_class.get(new_status_id, "name")

    logger.debug(
        "Checking issue status transition",
        extra={
            "nodeid": nodeid,
            "current_status": current_status_name,
            "new_status": new_status_name,
        },
    )

    if new_status_id not in allowed_statuses:
        logger.warning(
            "Invalid issue status transition rejected",
            extra={
                "nodeid": nodeid,
                "current_status": current_status_name,
                "new_status": new_status_name,
            },
        )
        raise Reject(f"Invalid status transition: {current_status_name} -> {new_status_name}")

    logger.debug(
        "Issue status transition validated",
        extra={
            "nodeid": nodeid,
            "current_status": current_status_name,
            "new_status": new_status_name,
        },
    )


def init(db):
    """
    Initialize the status workflow detector.

    Args:
        db: Database instance
    """
    # Register the detector for the issue class
    db.issue.audit("set", check_status_transition)
