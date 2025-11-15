# SPDX-FileCopyrightText: 2025 Georges Martin <jrjsmrtn@gmail.com>
# SPDX-License-Identifier: MIT

"""
Status workflow detector for enforcing valid issue status transitions.

This detector implements ITIL-inspired workflow rules:
- new (1) → in-progress (2)
- in-progress (2) → resolved (3)
- resolved (3) → closed (4)
- resolved (3) → in-progress (2) (reopening)

Invalid transitions (e.g., new → closed) are rejected.
"""


def check_status_transition(db, cl, nodeid, newvalues):
    """
    Enforce valid status transitions for issues.

    Args:
        db: Database instance
        cl: Issue class
        nodeid: Issue node ID (None for create)
        newvalues: Dictionary of new values being set

    Raises:
        ValueError: If the status transition is invalid
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

    # Define valid transitions (current_status_id -> [allowed_next_status_ids])
    # Status IDs: new=1, in-progress=2, resolved=3, closed=4
    VALID_TRANSITIONS = {
        "1": ["2"],  # new → in-progress
        "2": ["3"],  # in-progress → resolved
        "3": ["2", "4"],  # resolved → in-progress (reopen) or closed
        "4": [],  # closed is terminal (no transitions allowed)
    }

    # Check if transition is valid
    allowed_statuses = VALID_TRANSITIONS.get(current_status_id, [])

    if new_status_id not in allowed_statuses:
        # Get status names for better error messages
        status_class = db.getclass("status")
        current_status_name = status_class.get(current_status_id, "name")
        new_status_name = status_class.get(new_status_id, "name")

        raise ValueError(
            f"Invalid status transition: {current_status_name} -> {new_status_name}"
        )


def init(db):
    """
    Initialize the status workflow detector.

    Args:
        db: Database instance
    """
    # Register the detector for the issue class
    db.issue.audit("set", check_status_transition)
