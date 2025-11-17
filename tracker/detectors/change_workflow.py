# SPDX-FileCopyrightText: 2025 Georges Martin <jrjsmrtn@gmail.com>
# SPDX-License-Identifier: MIT

"""
Change workflow detector for enforcing valid change status transitions.

This detector implements ITIL-inspired change management workflow rules:
- planning → approved
- approved → implementing
- implementing → completed
- Any stage → cancelled (rejection/cancellation)

Invalid transitions (e.g., planning → completed) are rejected.
"""

import logging

from roundup.exceptions import Reject

logger = logging.getLogger(__name__)


def check_change_status_transition(db, cl, nodeid, newvalues):
    """
    Enforce valid status transitions for changes.

    Args:
        db: Database instance
        cl: Change class
        nodeid: Change node ID (None for create)
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
    status_class = db.getclass("changestatus")
    planning_id = status_class.lookup("planning")
    approved_id = status_class.lookup("approved")
    implementing_id = status_class.lookup("implementing")
    completed_id = status_class.lookup("completed")
    cancelled_id = status_class.lookup("cancelled")

    # Define valid transitions using looked-up IDs
    VALID_TRANSITIONS = {
        planning_id: [approved_id, cancelled_id],  # planning → approved or cancelled
        approved_id: [implementing_id, cancelled_id],  # approved → implementing or cancelled
        implementing_id: [completed_id, cancelled_id],  # implementing → completed or cancelled
        completed_id: [],  # completed is terminal (no transitions allowed)
        cancelled_id: [],  # cancelled is terminal (no transitions allowed)
    }

    # Check if transition is valid
    allowed_statuses = VALID_TRANSITIONS.get(current_status_id, [])

    # Get status names for logging
    current_status_name = status_class.get(current_status_id, "name")
    new_status_name = status_class.get(new_status_id, "name")

    logger.debug(
        "Checking change status transition",
        extra={
            "nodeid": nodeid,
            "current_status": current_status_name,
            "new_status": new_status_name,
        },
    )

    if new_status_id not in allowed_statuses:
        logger.warning(
            "Invalid change status transition rejected",
            extra={
                "nodeid": nodeid,
                "current_status": current_status_name,
                "new_status": new_status_name,
            },
        )
        raise Reject(f"Invalid status transition: {current_status_name} -> {new_status_name}")

    logger.debug(
        "Change status transition validated",
        extra={
            "nodeid": nodeid,
            "current_status": current_status_name,
            "new_status": new_status_name,
        },
    )


def init(db):
    """
    Initialize the change workflow detector.

    Args:
        db: Database instance
    """
    # Register the detector for the change class
    db.change.audit("set", check_change_status_transition)
