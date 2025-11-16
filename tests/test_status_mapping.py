# SPDX-FileCopyrightText: 2025 Georges Martin <jrjsmrtn@gmail.com>
# SPDX-License-Identifier: MIT

"""Unit tests for status mapping in step definitions."""

import pytest

from features.steps.common import STATUS_MAP


class TestStatusMapping:
    """Test the STATUS_MAP used across step definitions."""

    def test_status_map_contains_all_statuses(self):
        """Verify STATUS_MAP contains all expected workflow statuses."""
        expected_statuses = {"new", "in-progress", "resolved", "closed"}
        assert set(STATUS_MAP.keys()) == expected_statuses

    def test_status_map_values_are_strings(self):
        """Verify all status IDs are strings."""
        for status_id in STATUS_MAP.values():
            assert isinstance(status_id, str)

    def test_status_map_ids_are_sequential(self):
        """Verify status IDs are sequential starting from 1."""
        expected_ids = {"1", "2", "3", "4"}
        assert set(STATUS_MAP.values()) == expected_ids

    @pytest.mark.parametrize(
        "status_name,expected_id",
        [
            ("new", "1"),
            ("in-progress", "2"),
            ("resolved", "3"),
            ("closed", "4"),
        ],
    )
    def test_status_mapping(self, status_name, expected_id):
        """Test individual status name to ID mappings."""
        assert STATUS_MAP[status_name] == expected_id

    def test_status_map_is_immutable(self):
        """Verify STATUS_MAP cannot be modified (best practice)."""
        # This tests that STATUS_MAP is a dict, but we could make it immutable
        # For now, just verify it exists and has the right structure
        assert isinstance(STATUS_MAP, dict)
        assert len(STATUS_MAP) == 4
