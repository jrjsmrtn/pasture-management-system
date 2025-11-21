# SPDX-FileCopyrightText: 2025 Georges Martin <jrjsmrtn@gmail.com>
# SPDX-License-Identifier: MIT

"""
Email status parser detector for updating issue status from email subject.

This detector parses status directives from email subjects in the format:
[status=in-progress] or [status:in-progress]

When an email with such a directive creates or updates an issue, the issue
status is automatically updated to match the directive.
"""

import logging
import re

logger = logging.getLogger(__name__)


def parse_status_from_subject(db, cl, nodeid, oldvalues):
    """
    Parse status directive from message summary and update linked issue.

    Looks for patterns like [status=in-progress] or [status:in-progress]
    in the message summary (subject line) and updates the linked issue
    status accordingly.

    Args:
        db: Database instance
        cl: Message class
        nodeid: Message node ID
        oldvalues: Dictionary of old values (for update detection)
    """
    # Only process new messages
    if oldvalues:
        return

    # Get message summary (subject)
    try:
        summary = cl.get(nodeid, "summary")
    except (KeyError, IndexError):
        return

    if not summary:
        return

    # Parse status directive: [status=value] or [status:value]
    # Case-insensitive, allows hyphens in status names
    status_pattern = r"\[status[=:]([a-z][a-z\-]*)\]"
    match = re.search(status_pattern, summary, re.IGNORECASE)

    if not match:
        return

    status_name = match.group(1).lower()

    logger.debug(
        f"Found status directive in email subject",
        extra={
            "message_id": nodeid,
            "status_name": status_name,
        },
    )

    # Get linked issue IDs
    try:
        issue_ids = cl.get(nodeid, "issues")
    except (KeyError, IndexError):
        logger.debug("Message has no linked issues")
        return

    if not issue_ids:
        logger.debug("Message has no linked issues")
        return

    # Get status class and lookup status ID
    status_class = db.getclass("status")
    try:
        status_id = status_class.lookup(status_name)
    except KeyError:
        logger.warning(
            f"Invalid status name in email subject: {status_name}",
            extra={"message_id": nodeid, "status_name": status_name},
        )
        return

    # Update all linked issues
    issue_class = db.getclass("issue")
    for issue_id in issue_ids:
        try:
            current_status = issue_class.get(issue_id, "status")
            if current_status != status_id:
                issue_class.set(issue_id, status=status_id)
                logger.info(
                    f"Updated issue status from email directive",
                    extra={
                        "issue_id": issue_id,
                        "message_id": nodeid,
                        "status_name": status_name,
                    },
                )
        except Exception as e:
            logger.error(
                f"Failed to update issue status: {e}",
                extra={
                    "issue_id": issue_id,
                    "message_id": nodeid,
                    "status_name": status_name,
                },
            )


def init(db):
    """
    Initialize the email status parser detector.

    Args:
        db: Database instance
    """
    # Register the detector for the message class (react after creation)
    db.msg.react("create", parse_status_from_subject)
