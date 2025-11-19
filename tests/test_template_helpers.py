# SPDX-FileCopyrightText: 2025 Georges Martin <jrjsmrtn@gmail.com>
# SPDX-License-Identifier: MIT

"""Unit tests for template helper functions."""

import os
import sys
from unittest.mock import MagicMock, Mock

import pytest


# Add tracker extensions to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "tracker", "extensions"))

from template_helpers import filter_ci_ids_by_search, sort_ci_ids


class TestSortCIIds:
    """Test the sort_ci_ids function."""

    def _create_mock_field(self, value):
        """Create a mock field with .plain() method."""
        field = Mock()
        field.plain = Mock(return_value=value)
        return field

    def _create_mock_ci(self, id_str, name, ci_type, status, criticality):
        """Create a mock CI HTMLItem wrapper."""
        ci = Mock()
        ci.id = id_str
        ci.name = self._create_mock_field(name)
        ci.type = self._create_mock_field(ci_type)
        ci.status = self._create_mock_field(status)
        ci.criticality = self._create_mock_field(criticality)
        return ci

    @pytest.fixture
    def mock_db(self):
        """Create a mock database (not used in new implementation)."""
        return Mock()

    @pytest.fixture
    def mock_ci_ids(self):
        """Create mock CI HTMLItem objects."""
        # Create CIs with names: zulu, alpha, bravo
        ci1 = self._create_mock_ci("1", "zulu-server", "Server", "Active", "Medium")
        ci2 = self._create_mock_ci("2", "alpha-server", "Server", "Active", "High")
        ci3 = self._create_mock_ci("3", "bravo-server", "Server", "Active", "Low")
        return [ci1, ci2, ci3]

    def test_sort_by_name_ascending(self, mock_db, mock_ci_ids):
        """Test sorting CIs by name in ascending order."""
        result = sort_ci_ids(mock_db, mock_ci_ids, "name")

        # Should be: alpha(2), bravo(3), zulu(1)
        assert len(result) == 3
        assert result[0].id == "2"  # alpha
        assert result[1].id == "3"  # bravo
        assert result[2].id == "1"  # zulu

    def test_sort_by_name_descending(self, mock_db, mock_ci_ids):
        """Test sorting CIs by name in descending order."""
        result = sort_ci_ids(mock_db, mock_ci_ids, "-name")

        # Should be: zulu(1), bravo(3), alpha(2)
        assert len(result) == 3
        assert result[0].id == "1"  # zulu
        assert result[1].id == "3"  # bravo
        assert result[2].id == "2"  # alpha

    def test_sort_by_id_ascending(self, mock_db):
        """Test sorting CIs by ID in ascending order."""
        ci_ids = ["3", "1", "2"]

        result = sort_ci_ids(mock_db, ci_ids, "id")

        assert result == ["1", "2", "3"]

    def test_sort_by_id_descending(self, mock_db):
        """Test sorting CIs by ID in descending order."""
        ci_ids = ["1", "2", "3"]

        result = sort_ci_ids(mock_db, ci_ids, "-id")

        assert result == ["3", "2", "1"]

    def test_sort_default_no_param(self, mock_db):
        """Test default sorting when no sort parameter provided."""
        ci_ids = ["3", "1", "2"]

        result = sort_ci_ids(mock_db, ci_ids, None)

        # Default should be by ID ascending
        assert result == ["1", "2", "3"]

    def test_sort_empty_list(self, mock_db):
        """Test sorting an empty list."""
        result = sort_ci_ids(mock_db, [], "name")

        assert result == []

    def test_sort_with_htmlitem_wrapper(self, mock_db, mock_ci_ids):
        """Test sorting with Roundup HTMLItem wrappers."""
        # mock_ci_ids are already HTMLItem wrappers
        result = sort_ci_ids(mock_db, mock_ci_ids, "name")

        # Should return HTMLItems in sorted order: alpha(2), bravo(3), zulu(1)
        assert len(result) == 3
        assert result[0].id == "2"  # alpha
        assert result[1].id == "3"  # bravo
        assert result[2].id == "1"  # zulu

    def test_sort_case_insensitive(self, mock_db, mock_ci_ids):
        """Test that sorting is case-insensitive."""
        # Add a CI with uppercase name
        ci4 = self._create_mock_ci("4", "DELTA-server", "Server", "Active", "Medium")

        ci_ids = mock_ci_ids + [ci4]  # zulu, alpha, bravo, DELTA

        result = sort_ci_ids(mock_db, ci_ids, "name")

        # Should be: alpha(2), bravo(3), DELTA(4), zulu(1)
        assert len(result) == 4
        assert result[0].id == "2"  # alpha
        assert result[1].id == "3"  # bravo
        assert result[2].id == "4"  # DELTA
        assert result[3].id == "1"  # zulu

    def test_sort_with_none_values(self, mock_db):
        """Test sorting when some CIs have None for the sort field."""
        # Add a CI with no name
        ci4 = Mock()
        ci4.name = None
        ci4.type = "1"
        ci4.status = "1"
        ci4.criticality = "2"

        # Extend mock_db
        original_getnode = mock_db.ci.getnode

        def extended_getnode(id_str):
            if id_str == "4":
                return ci4
            return original_getnode(id_str)

        mock_db.ci.getnode = extended_getnode

        ci_ids = ["1", "2", "3", "4"]

        result = sort_ci_ids(mock_db, ci_ids, "name")

        # None values should sort last
        # Should be: alpha(2), bravo(3), zulu(1), None(4)
        assert result[-1] == "4"
        assert set(result[:3]) == {"1", "2", "3"}


class TestFilterCIIdsBySearch:
    """Test the filter_ci_ids_by_search function."""

    def _create_mock_field(self, value):
        """Create a mock field with .plain() method."""
        field = Mock()
        field.plain = Mock(return_value=value)
        return field

    def _create_mock_ci(self, id_str, name, location):
        """Create a mock CI HTMLItem wrapper."""
        ci = Mock()
        ci.id = id_str
        ci.name = self._create_mock_field(name)
        ci.location = self._create_mock_field(location)
        return ci

    @pytest.fixture
    def mock_db(self):
        """Create a mock database (not used in new implementation)."""
        return Mock()

    @pytest.fixture
    def mock_ci_ids(self):
        """Create mock CI HTMLItem objects."""
        ci1 = self._create_mock_ci("1", "web-server-prod", "datacenter-1")
        ci2 = self._create_mock_ci("2", "db-server-prod", "datacenter-2")
        ci3 = self._create_mock_ci("3", "web-server-dev", "office")
        return [ci1, ci2, ci3]

    def test_filter_by_name(self, mock_db, mock_ci_ids):
        """Test filtering CIs by name."""
        result = filter_ci_ids_by_search(mock_db, mock_ci_ids, "web")

        # Should match web-server-prod and web-server-dev
        assert len(result) == 2
        assert set([ci.id for ci in result]) == {"1", "3"}

    def test_filter_case_insensitive(self, mock_db, mock_ci_ids):
        """Test that filtering is case-insensitive."""
        result = filter_ci_ids_by_search(mock_db, mock_ci_ids, "WEB")

        assert len(result) == 2
        assert set([ci.id for ci in result]) == {"1", "3"}

    def test_filter_by_location(self, mock_db, mock_ci_ids):
        """Test filtering by location field."""
        result = filter_ci_ids_by_search(mock_db, mock_ci_ids, "datacenter")

        # Should match datacenter-1 and datacenter-2
        assert len(result) == 2
        assert set([ci.id for ci in result]) == {"1", "2"}

    def test_filter_no_matches(self, mock_db, mock_ci_ids):
        """Test filtering with no matches."""
        result = filter_ci_ids_by_search(mock_db, mock_ci_ids, "nonexistent")

        assert result == []

    def test_filter_empty_search_term(self, mock_db, mock_ci_ids):
        """Test filtering with empty search term."""
        result = filter_ci_ids_by_search(mock_db, mock_ci_ids, "")

        # Empty search should return all CIs
        assert len(result) == 3
        assert set([ci.id for ci in result]) == {"1", "2", "3"}

    def test_filter_none_search_term(self, mock_db, mock_ci_ids):
        """Test filtering with None search term."""
        result = filter_ci_ids_by_search(mock_db, mock_ci_ids, None)

        # None search should return all CIs
        assert len(result) == 3
        assert set([ci.id for ci in result]) == {"1", "2", "3"}

    def test_filter_empty_ci_list(self, mock_db):
        """Test filtering an empty CI list."""
        result = filter_ci_ids_by_search(mock_db, [], "search")

        assert result == []
