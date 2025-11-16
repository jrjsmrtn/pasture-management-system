# SPDX-FileCopyrightText: 2025 Georges Martin <jrjsmrtn@gmail.com>
# SPDX-License-Identifier: MIT

"""Unit tests for change request mappings in step definitions."""

import pytest

from features.steps.change_list_steps import (
    CHANGECATEGORY_MAP,
    CHANGEPRIORITY_MAP,
    CHANGESTATUS_MAP,
)


class TestChangePriorityMapping:
    """Test CHANGEPRIORITY_MAP used in change request steps."""

    def test_priority_map_contains_all_priorities(self):
        """Verify CHANGEPRIORITY_MAP contains all expected priorities."""
        expected_priorities = {"low", "medium", "high", "critical"}
        assert set(CHANGEPRIORITY_MAP.keys()) == expected_priorities

    def test_priority_map_ids_are_sequential(self):
        """Verify priority IDs are sequential starting from 1."""
        expected_ids = {"1", "2", "3", "4"}
        assert set(CHANGEPRIORITY_MAP.values()) == expected_ids

    @pytest.mark.parametrize(
        "priority_name,expected_id",
        [
            ("low", "1"),
            ("medium", "2"),
            ("high", "3"),
            ("critical", "4"),
        ],
    )
    def test_priority_mapping(self, priority_name, expected_id):
        """Test individual priority name to ID mappings."""
        assert CHANGEPRIORITY_MAP[priority_name] == expected_id


class TestChangeCategoryMapping:
    """Test CHANGECATEGORY_MAP used in change request steps."""

    def test_category_map_contains_all_categories(self):
        """Verify CHANGECATEGORY_MAP contains all expected categories."""
        expected_categories = {"software", "hardware", "configuration", "network"}
        assert set(CHANGECATEGORY_MAP.keys()) == expected_categories

    def test_category_map_ids_are_sequential(self):
        """Verify category IDs are sequential starting from 1."""
        expected_ids = {"1", "2", "3", "4"}
        assert set(CHANGECATEGORY_MAP.values()) == expected_ids

    @pytest.mark.parametrize(
        "category_name,expected_id",
        [
            ("software", "1"),
            ("hardware", "2"),
            ("configuration", "3"),
            ("network", "4"),
        ],
    )
    def test_category_mapping(self, category_name, expected_id):
        """Test individual category name to ID mappings."""
        assert CHANGECATEGORY_MAP[category_name] == expected_id


class TestChangeStatusMapping:
    """Test CHANGESTATUS_MAP used in change request steps."""

    def test_status_map_contains_all_statuses(self):
        """Verify CHANGESTATUS_MAP contains all expected statuses."""
        expected_statuses = {"planning", "approved", "implementing", "completed", "cancelled"}
        assert set(CHANGESTATUS_MAP.keys()) == expected_statuses

    def test_status_map_ids_are_sequential(self):
        """Verify status IDs are sequential starting from 1."""
        expected_ids = {"1", "2", "3", "4", "5"}
        assert set(CHANGESTATUS_MAP.values()) == expected_ids

    @pytest.mark.parametrize(
        "status_name,expected_id",
        [
            ("planning", "1"),
            ("approved", "2"),
            ("implementing", "3"),
            ("completed", "4"),
            ("cancelled", "5"),
        ],
    )
    def test_status_mapping(self, status_name, expected_id):
        """Test individual status name to ID mappings."""
        assert CHANGESTATUS_MAP[status_name] == expected_id


class TestMappingConsistency:
    """Test consistency across all change-related mappings."""

    def test_all_mappings_use_string_ids(self):
        """Verify all mappings use string IDs (not integers)."""
        for mapping in [CHANGEPRIORITY_MAP, CHANGECATEGORY_MAP, CHANGESTATUS_MAP]:
            for value in mapping.values():
                assert isinstance(value, str), f"Expected string ID, got {type(value)}"

    def test_no_overlapping_ids(self):
        """Verify mappings don't share IDs (they're in different tables)."""
        # This is expected since they're different database tables
        # Just verify each mapping has unique IDs within itself
        for mapping_name, mapping in [
            ("CHANGEPRIORITY_MAP", CHANGEPRIORITY_MAP),
            ("CHANGECATEGORY_MAP", CHANGECATEGORY_MAP),
            ("CHANGESTATUS_MAP", CHANGESTATUS_MAP),
        ]:
            ids = list(mapping.values())
            assert len(ids) == len(set(ids)), f"{mapping_name} has duplicate IDs"
