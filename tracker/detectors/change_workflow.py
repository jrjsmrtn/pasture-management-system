# SPDX-FileCopyrightText: 2025 Georges Martin <jrjsmrtn@gmail.com>
# SPDX-License-Identifier: MIT

"""
Change workflow detector for enforcing valid change status transitions.

This detector implements ITIL-inspired change management workflow rules:
- planning (1) → approved (2)
- approved (2) → implementing (3)
- implementing (3) → completed (4)
- Any stage → cancelled (5) (rejection/cancellation)

Invalid transitions (e.g., planning → completed) are rejected.
"""


def check_change_status_transition(db, cl, nodeid, newvalues):
    """
    Enforce valid status transitions for changes.

    Args:
        db: Database instance
        cl: Change class
        nodeid: Change node ID (None for create)
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
    # Status IDs: planning=1, approved=2, implementing=3, completed=4, cancelled=5
    VALID_TRANSITIONS = {
        "1": ["2", "5"],  # planning → approved or cancelled
        "2": ["3", "5"],  # approved → implementing or cancelled
        "3": ["4", "5"],  # implementing → completed or cancelled
        "4": [],  # completed is terminal (no transitions allowed)
        "5": [],  # cancelled is terminal (no transitions allowed)
    }

    # Check if transition is valid
    allowed_statuses = VALID_TRANSITIONS.get(current_status_id, [])

    if new_status_id not in allowed_statuses:
        # Get status names for better error messages
        status_class = db.getclass("changestatus")
        current_status_name = status_class.get(current_status_id, "name")
        new_status_name = status_class.get(new_status_id, "name")

        raise ValueError(f"Invalid status transition: {current_status_name} -> {new_status_name}")


def init(db):
    """
    Initialize the change workflow detector.

    Args:
        db: Database instance
    """
    # Register the detector for the change class
    db.change.audit("set", check_change_status_transition)
