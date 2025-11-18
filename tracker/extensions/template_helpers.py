# SPDX-FileCopyrightText: 2025 Georges Martin <jrjsmrtn@gmail.com>
# SPDX-License-Identifier: MIT

"""Template helper functions for Roundup TAL templates."""


def sort_ci_ids(db, ci_ids, sort_param=None):
    """
    Sort CI IDs based on a sort parameter.

    Args:
        db: Roundup database instance
        ci_ids: List of CI IDs (may be strings or Roundup HTMLItem objects)
        sort_param: Sort parameter string (e.g., 'name', '-name', 'type')
                   Prefix with '-' for descending order

    Returns:
        List of sorted CI IDs in the same type as input

    Examples:
        sort_ci_ids(db, ['1', '2', '3'], 'name')      # Sort by name ascending
        sort_ci_ids(db, ['1', '2', '3'], '-name')     # Sort by name descending
        sort_ci_ids(db, ['1', '2', '3'], None)        # Default sort by ID
    """
    if not ci_ids:
        return []

    # Helper to extract plain ID string from Roundup HTMLItem or plain string
    def get_id_str(ci_id):
        """Extract plain ID string from CI ID (handles HTMLItem wrapper)."""
        if hasattr(ci_id, "id"):
            return str(ci_id.id)
        return str(ci_id)

    # Parse sort parameter
    if not sort_param:
        # Default: sort by ID ascending
        return sorted(ci_ids, key=lambda x: int(get_id_str(x)))

    # Check for descending order (prefix with '-')
    descending = sort_param.startswith("-")
    field_name = sort_param[1:] if descending else sort_param

    # Special case: sort by ID numerically
    if field_name == "id":
        return sorted(ci_ids, key=lambda x: int(get_id_str(x)), reverse=descending)

    # Sort by field value
    def get_sort_key(ci_id):
        """Extract sort key from CI node."""
        try:
            # Extract plain ID string (handles HTMLItem wrapper)
            id_str = get_id_str(ci_id)
            node = db.ci.getnode(id_str)
            value = getattr(node, field_name, None)

            # Handle None values (sort them last)
            if value is None:
                return ("~", id_str)  # '~' sorts after letters

            # Handle Roundup Link/Multilink objects
            if hasattr(value, "plain"):
                return (str(value.plain()).lower(), id_str)

            # Handle regular values
            return (str(value).lower(), id_str)

        except (AttributeError, KeyError):
            # If field doesn't exist, sort by CI ID
            return (id_str, id_str)

    return sorted(ci_ids, key=get_sort_key, reverse=descending)


def filter_ci_ids_by_search(db, ci_ids, search_term):
    """
    Filter CI IDs by search term (name or location).

    Args:
        db: Roundup database instance
        ci_ids: List of CI IDs to filter
        search_term: Search term (empty string means no filtering)

    Returns:
        List of filtered CI IDs
    """
    if not search_term:
        return list(ci_ids)

    search_lower = search_term.lower()
    result = []

    for ci_id in ci_ids:
        # Extract plain ID string (handles HTMLItem wrapper)
        if hasattr(ci_id, "id"):
            id_str = str(ci_id.id)
        else:
            id_str = str(ci_id)

        try:
            node = db.ci.getnode(id_str)
            # Search in name and location
            name = (node.name or "").lower()
            location = (node.location or "").lower()

            if search_lower in name or search_lower in location:
                result.append(ci_id)
        except (AttributeError, KeyError):
            # Skip CIs we can't access
            continue

    return result


def init(instance):
    """
    Initialize template helpers for this Roundup instance.

    This function is called by Roundup during instance initialization.
    Register helper functions that should be available in TAL templates.
    """
    # Register helper functions
    instance.registerUtil("sort_ci_ids", sort_ci_ids)
    instance.registerUtil("filter_ci_ids_by_search", filter_ci_ids_by_search)
