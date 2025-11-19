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

    # Create sort tuples without using key function (TAL/Roundup compatibility)
    # Build list of (sort_key, ci_id) tuples
    # Note: ci_id objects are already _HTMLItem wrappers with all properties
    sort_tuples = []

    for ci_id in ci_ids:
        try:
            id_str = get_id_str(ci_id)

            # Access field directly from HTMLItem wrapper
            value = getattr(ci_id, field_name, None)

            # For fields with ordering (criticality, status, type), use mappings
            # This is necessary because accessing order values from HTMLItem wrappers
            # is complex in the Roundup TAL context
            order_mappings = {
                "criticality": {"Very Low": 1, "Low": 2, "Medium": 3, "High": 4, "Very High": 5},
                "status": {
                    "Planning": 1,
                    "Ordered": 2,
                    "In Stock": 3,
                    "Deployed": 4,
                    "Active": 5,
                    "Maintenance": 6,
                    "Retired": 7,
                },
                "type": {
                    "Server": 1,
                    "Network Device": 2,
                    "Storage": 3,
                    "Software": 4,
                    "Service": 5,
                    "Virtual Machine": 6,
                },
            }

            # Get the sort value
            if value is not None and hasattr(value, "plain"):
                plain_value = value.plain()
                # Check if this field has an order mapping
                if field_name in order_mappings and plain_value in order_mappings[field_name]:
                    sort_value = order_mappings[field_name][plain_value]
                else:
                    sort_value = plain_value
            elif value is not None:
                sort_value = str(value)
            else:
                sort_value = value

            # Create sort key
            if sort_value is None or sort_value == "":
                sort_key = ("~", id_str)  # None/empty values sort last
            elif isinstance(sort_value, str):
                sort_key = (sort_value.lower(), id_str)
            elif isinstance(sort_value, (int, float)):
                sort_key = (sort_value, id_str)
            else:
                sort_key = (str(sort_value), id_str)

            sort_tuples.append((sort_key, ci_id))
        except (AttributeError, KeyError):
            # If field doesn't exist, sort by CI ID
            sort_tuples.append((id_str, ci_id))

    # Sort the tuples
    sort_tuples.sort(reverse=descending)

    # Extract just the CI IDs
    return [ci_id for _, ci_id in sort_tuples]


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
        try:
            # ci_id is already an HTMLItem object with the CI data
            # Access name and location directly from the HTMLItem
            name = ""
            if hasattr(ci_id, "name") and ci_id.name:
                if hasattr(ci_id.name, "plain"):
                    name = ci_id.name.plain()
                else:
                    name = str(ci_id.name)
            name = name.lower()

            location = ""
            if hasattr(ci_id, "location") and ci_id.location:
                if hasattr(ci_id.location, "plain"):
                    location = ci_id.location.plain()
                else:
                    location = str(ci_id.location)
            location = location.lower()

            if search_lower in name or search_lower in location:
                result.append(ci_id)
        except (AttributeError, KeyError, Exception):
            # Skip CIs we can't access or have errors
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
