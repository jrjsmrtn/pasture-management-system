# SPDX-FileCopyrightText: 2025 Georges Martin <jrjsmrtn@gmail.com>
# SPDX-License-Identifier: MIT

"""Unit tests for test data cleanup functionality."""

import os
from unittest.mock import MagicMock, patch

import pytest

from features.environment import _cleanup_test_data


class TestCleanupTestData:
    """Test the _cleanup_test_data function."""

    @patch("features.environment.subprocess.run")
    @patch.dict(os.environ, {"CLEANUP_TEST_DATA": "true"})
    def test_cleanup_single_issue(self, mock_run):
        """Test cleanup of a single issue."""
        context = MagicMock(spec=["tracker_dir", "created_issue_id"])
        context.tracker_dir = "tracker"
        context.created_issue_id = "issue5"

        _cleanup_test_data(context)

        mock_run.assert_called_once_with(
            ["roundup-admin", "-i", "tracker", "retire", "issue5"],
            capture_output=True,
            timeout=10,
            check=False,
        )

    @patch("features.environment.subprocess.run")
    @patch.dict(os.environ, {"CLEANUP_TEST_DATA": "true"})
    def test_cleanup_multiple_issues(self, mock_run):
        """Test cleanup of multiple issues."""
        context = MagicMock(spec=["tracker_dir", "test_issue_ids"])
        context.tracker_dir = "tracker"
        context.test_issue_ids = {"5", "6", "7"}

        _cleanup_test_data(context)

        # Should be called 3 times, once for each issue
        assert mock_run.call_count == 3
        calls = [call[0][0][4] for call in mock_run.call_args_list]
        assert set(calls) == {"issue5", "issue6", "issue7"}

    @patch("features.environment.subprocess.run")
    @patch.dict(os.environ, {"CLEANUP_TEST_DATA": "true"})
    def test_cleanup_single_change(self, mock_run):
        """Test cleanup of a single change."""
        context = MagicMock(spec=["tracker_dir", "created_change_id"])
        context.tracker_dir = "tracker"
        context.created_change_id = "change10"

        _cleanup_test_data(context)

        mock_run.assert_called_once_with(
            ["roundup-admin", "-i", "tracker", "retire", "change10"],
            capture_output=True,
            timeout=10,
            check=False,
        )

    @patch("features.environment.subprocess.run")
    @patch.dict(os.environ, {"CLEANUP_TEST_DATA": "true"})
    def test_cleanup_multiple_changes(self, mock_run):
        """Test cleanup of multiple changes."""
        context = MagicMock(spec=["tracker_dir", "test_change_ids"])
        context.tracker_dir = "tracker"
        context.test_change_ids = {"10", "11", "12"}

        _cleanup_test_data(context)

        # Should be called 3 times, once for each change
        assert mock_run.call_count == 3
        calls = [call[0][0][4] for call in mock_run.call_args_list]
        assert set(calls) == {"change10", "change11", "change12"}

    @patch("features.environment.subprocess.run")
    @patch.dict(os.environ, {"CLEANUP_TEST_DATA": "true"})
    def test_cleanup_issues_and_changes(self, mock_run):
        """Test cleanup of both issues and changes."""
        context = MagicMock(spec=["tracker_dir", "test_issue_ids", "test_change_ids"])
        context.tracker_dir = "tracker"
        context.test_issue_ids = {"5", "6"}
        context.test_change_ids = {"10", "11"}

        _cleanup_test_data(context)

        # Should be called 4 times total
        assert mock_run.call_count == 4

        # Verify both issues and changes were cleaned
        calls = [call[0][0][4] for call in mock_run.call_args_list]
        assert "issue5" in calls
        assert "issue6" in calls
        assert "change10" in calls
        assert "change11" in calls

    @patch("features.environment.subprocess.run")
    @patch.dict(os.environ, {"CLEANUP_TEST_DATA": "false"})
    def test_cleanup_disabled(self, mock_run):
        """Test that cleanup can be disabled via environment variable."""
        context = MagicMock(spec=["tracker_dir", "test_issue_ids", "test_change_ids"])
        context.tracker_dir = "tracker"
        context.test_issue_ids = {"5"}
        context.test_change_ids = {"10"}

        _cleanup_test_data(context)

        # Should not call subprocess.run when cleanup is disabled
        mock_run.assert_not_called()

    @patch("features.environment.subprocess.run")
    @patch.dict(os.environ, {"CLEANUP_TEST_DATA": "true"})
    def test_cleanup_handles_exceptions(self, mock_run):
        """Test that cleanup handles exceptions gracefully."""
        context = MagicMock(spec=["tracker_dir", "test_issue_ids"])
        context.tracker_dir = "tracker"
        context.test_issue_ids = {"5", "6"}

        # Make first call raise exception, second call succeed
        mock_run.side_effect = [Exception("DB Error"), None]

        # Should not raise exception
        _cleanup_test_data(context)

        # Both issues should be attempted
        assert mock_run.call_count == 2

    @patch("features.environment.subprocess.run")
    @patch.dict(os.environ, {"CLEANUP_TEST_DATA": "true"})
    def test_cleanup_extracts_numeric_ids(self, mock_run):
        """Test that cleanup extracts numeric IDs from prefixed IDs."""
        context = MagicMock(spec=["tracker_dir", "created_issue_id", "created_change_id"])
        context.tracker_dir = "tracker"
        context.created_issue_id = "issue123"
        context.created_change_id = "change456"

        _cleanup_test_data(context)

        # Should extract numeric IDs
        calls = [call[0][0][4] for call in mock_run.call_args_list]
        assert "issue123" in calls
        assert "change456" in calls

    @patch("features.environment.subprocess.run")
    @patch.dict(os.environ, {"CLEANUP_TEST_DATA": "true"})
    def test_cleanup_no_data_to_clean(self, mock_run):
        """Test that cleanup handles context with no test data."""
        context = MagicMock(spec=["tracker_dir"])
        context.tracker_dir = "tracker"
        # No test data attributes

        _cleanup_test_data(context)

        # Should not call subprocess.run when no data to clean
        mock_run.assert_not_called()

    @patch("features.environment.subprocess.run")
    @patch.dict(os.environ, {"CLEANUP_TEST_DATA": "true"})
    def test_cleanup_uses_correct_tracker_dir(self, mock_run):
        """Test that cleanup uses the correct tracker directory."""
        context = MagicMock(spec=["tracker_dir", "created_issue_id"])
        context.tracker_dir = "custom_tracker"
        context.created_issue_id = "5"

        _cleanup_test_data(context)

        # Should use custom tracker directory
        mock_run.assert_called_once()
        call_args = mock_run.call_args[0][0]
        assert call_args[2] == "custom_tracker"

    @patch("features.environment.subprocess.run")
    @patch.dict(os.environ, {"CLEANUP_TEST_DATA": "true"})
    def test_cleanup_deduplicates_ids(self, mock_run):
        """Test that cleanup deduplicates IDs when set from multiple sources."""
        context = MagicMock(
            spec=["tracker_dir", "created_issue_id", "test_issue_ids", "api_issue_id"]
        )
        context.tracker_dir = "tracker"
        context.created_issue_id = "5"
        context.test_issue_ids = {"5", "6"}  # ID 5 appears twice
        context.api_issue_id = "5"  # ID 5 appears three times

        _cleanup_test_data(context)

        # Should only clean each ID once
        calls = [call[0][0][4] for call in mock_run.call_args_list]
        assert calls.count("issue5") == 1
        assert calls.count("issue6") == 1
        assert mock_run.call_count == 2
