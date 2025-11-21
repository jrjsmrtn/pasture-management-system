# SPDX-FileCopyrightText: 2025 Georges Martin <jrjsmrtn@gmail.com>
# SPDX-License-Identifier: MIT

"""
Issue defaults detector for setting default values on issue creation.

This detector ensures that all issues have sensible default values:
- status: "new" (if not already set)
- priority: Can be left as None for "no priority"
"""

import logging

logger = logging.getLogger(__name__)


def set_issue_defaults(db, cl, nodeid, newvalues):
    """
    Set default values for new issues.

    Args:
        db: Database instance
        cl: Issue class
        nodeid: Issue node ID (None for creation)
        newvalues: Dictionary of new values being set
    """
    # Only set defaults on creation
    if nodeid is not None:
        return

    # Set default status to "new" if not already set
    if "status" not in newvalues or newvalues["status"] is None:
        try:
            status_class = db.getclass("status")
            new_status_id = status_class.lookup("new")
            newvalues["status"] = new_status_id
            logger.debug(
                "Set default status 'new' for new issue",
                extra={"nodeid": nodeid},
            )
        except KeyError:
            logger.warning("Could not find 'new' status in database")


def init(db):
    """
    Initialize the issue defaults detector.

    Args:
        db: Database instance
    """
    # Register the detector for the issue class (audit before creation)
    db.issue.audit("create", set_issue_defaults)
