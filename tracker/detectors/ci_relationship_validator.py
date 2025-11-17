# SPDX-FileCopyrightText: 2025 Georges Martin <jrjsmrtn@gmail.com>
# SPDX-License-Identifier: MIT

"""
CI Relationship Validator Detector

Validates CI relationships to prevent circular dependencies and ensure
data integrity in the CMDB.
"""

import logging
from roundup.exceptions import Reject

logger = logging.getLogger(__name__)


def has_circular_dependency(db, source_ci, target_ci, visited=None):
    """
    Check if creating a relationship would create a circular dependency.

    Args:
        db: Database instance
        source_ci: Source CI ID
        target_ci: Target CI ID
        visited: Set of visited CI IDs (for recursion)

    Returns:
        bool: True if circular dependency detected, False otherwise
    """
    if visited is None:
        visited = set()

    # If target CI is the same as source, it's circular
    if source_ci == target_ci:
        return True

    # If we've already visited this CI, we have a cycle
    if target_ci in visited:
        return True

    # Mark this CI as visited
    visited.add(target_ci)

    # Get all relationships where target_ci is the source
    # (i.e., CIs that target_ci depends on)
    relationships = db.cirelationship.filter(None, {"source_ci": target_ci})

    for rel_id in relationships:
        rel = db.cirelationship.getnode(rel_id)
        next_target = rel.target_ci

        # Recursively check for circular dependencies
        if has_circular_dependency(db, source_ci, next_target, visited.copy()):
            return True

    return False


def validate_ci_relationship(db, cl, nodeid, newvalues):
    """
    Validate CI relationship before creation/modification.

    Checks for:
    1. Circular dependencies
    2. Self-referencing relationships
    3. Duplicate relationships

    Args:
        db: Database instance
        cl: Class being audited (cirelationship)
        nodeid: Node ID (None for new items)
        newvalues: Dictionary of new/changed values
    """
    logger.info(
        "CI relationship validator called",
        extra={
            "nodeid": nodeid,
            "newvalues": newvalues,
            "action": "create" if nodeid is None else "update",
        },
    )

    # Only validate on create or when relationship changes
    if nodeid and not (
        "source_ci" in newvalues or "target_ci" in newvalues or "relationship_type" in newvalues
    ):
        logger.debug(
            "Skipping validation - no relationship field changes", extra={"nodeid": nodeid}
        )
        return

    # Get the relationship values
    if nodeid:
        # Editing existing relationship
        source_ci = newvalues.get("source_ci", cl.get(nodeid, "source_ci"))
        target_ci = newvalues.get("target_ci", cl.get(nodeid, "target_ci"))
        relationship_type = newvalues.get("relationship_type", cl.get(nodeid, "relationship_type"))
    else:
        # Creating new relationship
        source_ci = newvalues.get("source_ci")
        target_ci = newvalues.get("target_ci")
        relationship_type = newvalues.get("relationship_type")

    # Ensure required fields are present
    if not source_ci or not target_ci or not relationship_type:
        raise Reject("source_ci, target_ci, and relationship_type are required fields")

    # Check for self-referencing relationship
    logger.debug("Checking self-reference", extra={"source_ci": source_ci, "target_ci": target_ci})
    if source_ci == target_ci:
        logger.warning(
            "Validation failed: self-referencing relationship",
            extra={"source_ci": source_ci, "target_ci": target_ci, "validation": "self_reference"},
        )
        raise Reject("A CI cannot have a relationship with itself")

    # Check for circular dependencies
    logger.debug(
        "Checking circular dependency", extra={"source_ci": source_ci, "target_ci": target_ci}
    )
    if has_circular_dependency(db, source_ci, target_ci):
        logger.warning(
            "Validation failed: circular dependency detected",
            extra={
                "source_ci": source_ci,
                "target_ci": target_ci,
                "validation": "circular_dependency",
            },
        )
        raise Reject(
            "Circular dependency detected. This relationship would create a cycle "
            "in the dependency graph."
        )
    logger.debug("No circular dependency found")

    # Check for duplicate relationships (same source, target, and type)
    logger.debug(
        "Checking for duplicate relationships",
        extra={
            "source_ci": source_ci,
            "target_ci": target_ci,
            "relationship_type": relationship_type,
        },
    )
    existing_rels = db.cirelationship.filter(
        None,
        {"source_ci": source_ci, "target_ci": target_ci, "relationship_type": relationship_type},
    )

    # If editing, exclude the current relationship from duplicates check
    if nodeid:
        existing_rels = [rel for rel in existing_rels if rel != nodeid]

    if existing_rels:
        logger.warning(
            "Validation failed: duplicate relationship",
            extra={
                "source_ci": source_ci,
                "target_ci": target_ci,
                "relationship_type": relationship_type,
                "existing_rels": existing_rels,
                "validation": "duplicate",
            },
        )
        raise Reject("A relationship with the same source, target, and type already exists")

    logger.info(
        "Validation passed - relationship is valid",
        extra={
            "source_ci": source_ci,
            "target_ci": target_ci,
            "relationship_type": relationship_type,
        },
    )


def init(db):
    """Initialize the CI relationship validator detector."""
    db.cirelationship.audit("create", validate_ci_relationship)
    db.cirelationship.audit("set", validate_ci_relationship)
