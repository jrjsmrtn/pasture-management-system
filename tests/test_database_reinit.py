# SPDX-FileCopyrightText: 2025 Georges Martin <jrjsmrtn@gmail.com>
# SPDX-License-Identifier: MIT

"""Unit tests for database reinitialization functionality."""

import os
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from features.environment import _reinitialize_database


class TestDatabaseReinitialization:
    """Test the _reinitialize_database function."""

    @patch("features.environment.subprocess.Popen")
    @patch("features.environment.shutil.rmtree")
    @patch("features.environment.Path.exists")
    @patch.dict(os.environ, {"CLEANUP_TEST_DATA": "true"})
    def test_reinitialize_deletes_and_recreates_db(self, mock_exists, mock_rmtree, mock_popen):
        """Test that reinitialize deletes db directory and runs initialise."""
        context = MagicMock(spec=["tracker_dir"])
        context.tracker_dir = "tracker"

        # Mock database exists
        mock_exists.return_value = True

        # Mock successful initialization
        mock_process = MagicMock()
        mock_process.communicate.return_value = ("Success", "")
        mock_process.returncode = 0
        mock_popen.return_value = mock_process

        _reinitialize_database(context)

        # Should delete database directory
        mock_rmtree.assert_called_once()

        # Should run roundup-admin initialise
        mock_popen.assert_called_once_with(
            ["roundup-admin", "-i", "tracker", "initialise"],
            stdin=-1,  # subprocess.PIPE
            stdout=-1,
            stderr=-1,
            text=True,
        )

        # Should provide admin password
        mock_process.communicate.assert_called_once_with(input="admin\nadmin\n", timeout=30)

    @patch("features.environment.subprocess.Popen")
    @patch("features.environment.shutil.rmtree")
    @patch("features.environment.Path.exists")
    @patch.dict(os.environ, {"CLEANUP_TEST_DATA": "false"})
    def test_reinitialize_respects_env_var(self, mock_exists, mock_rmtree, mock_popen):
        """Test that reinitialize can be disabled via environment variable."""
        context = MagicMock(spec=["tracker_dir"])
        context.tracker_dir = "tracker"

        _reinitialize_database(context)

        # Should not delete or reinitialize when disabled
        mock_exists.assert_not_called()
        mock_rmtree.assert_not_called()
        mock_popen.assert_not_called()

    @patch("features.environment.subprocess.Popen")
    @patch("features.environment.shutil.rmtree")
    @patch("features.environment.Path.exists")
    @patch.dict(os.environ, {"CLEANUP_TEST_DATA": "true"})
    def test_reinitialize_skips_delete_if_db_missing(self, mock_exists, mock_rmtree, mock_popen):
        """Test that reinitialize skips delete if database doesn't exist."""
        context = MagicMock(spec=["tracker_dir"])
        context.tracker_dir = "tracker"

        # Mock database doesn't exist
        mock_exists.return_value = False

        # Mock successful initialization
        mock_process = MagicMock()
        mock_process.communicate.return_value = ("Success", "")
        mock_process.returncode = 0
        mock_popen.return_value = mock_process

        _reinitialize_database(context)

        # Should not delete if db doesn't exist
        mock_rmtree.assert_not_called()

        # But should still run initialise
        mock_popen.assert_called_once()

    @patch("features.environment.subprocess.Popen")
    @patch("features.environment.shutil.rmtree")
    @patch("features.environment.Path.exists")
    @patch.dict(os.environ, {"CLEANUP_TEST_DATA": "true"})
    def test_reinitialize_handles_exceptions_gracefully(self, mock_exists, mock_rmtree, mock_popen):
        """Test that reinitialize handles exceptions without failing."""
        context = MagicMock(spec=["tracker_dir"])
        context.tracker_dir = "tracker"

        # Mock database exists
        mock_exists.return_value = True

        # Mock rmtree raises exception
        mock_rmtree.side_effect = Exception("Permission denied")

        # Should not raise exception
        _reinitialize_database(context)

        # rmtree should have been attempted
        mock_rmtree.assert_called_once()

    @patch("features.environment.subprocess.Popen")
    @patch("features.environment.shutil.rmtree")
    @patch("features.environment.Path.exists")
    @patch.dict(os.environ, {"CLEANUP_TEST_DATA": "true"})
    def test_reinitialize_uses_correct_tracker_dir(self, mock_exists, mock_rmtree, mock_popen):
        """Test that reinitialize uses the correct tracker directory."""
        context = MagicMock(spec=["tracker_dir"])
        context.tracker_dir = "custom_tracker"

        # Mock database exists
        mock_exists.return_value = True

        # Mock successful initialization
        mock_process = MagicMock()
        mock_process.communicate.return_value = ("Success", "")
        mock_process.returncode = 0
        mock_popen.return_value = mock_process

        _reinitialize_database(context)

        # Should use custom tracker directory
        call_args = mock_popen.call_args[0][0]
        assert call_args[2] == "custom_tracker"

    @patch("features.environment.subprocess.Popen")
    @patch("features.environment.shutil.rmtree")
    @patch("features.environment.Path.exists")
    @patch.dict(os.environ, {"CLEANUP_TEST_DATA": "true"})
    def test_reinitialize_handles_init_failure(self, mock_exists, mock_rmtree, mock_popen):
        """Test that reinitialize handles initialization failure gracefully."""
        context = MagicMock(spec=["tracker_dir"])
        context.tracker_dir = "tracker"

        # Mock database exists
        mock_exists.return_value = True

        # Mock failed initialization
        mock_process = MagicMock()
        mock_process.communicate.return_value = ("", "Error: Database locked")
        mock_process.returncode = 1
        mock_popen.return_value = mock_process

        # Should not raise exception even if init fails
        _reinitialize_database(context)

        # Should have attempted deletion and init
        mock_rmtree.assert_called_once()
        mock_popen.assert_called_once()

    @patch("features.environment.subprocess.Popen")
    @patch("features.environment.shutil.rmtree")
    @patch("features.environment.Path.exists")
    @patch.dict(os.environ, {"CLEANUP_TEST_DATA": "true"})
    def test_reinitialize_uses_default_tracker_dir(self, mock_exists, mock_rmtree, mock_popen):
        """Test that reinitialize uses 'tracker' as default directory."""
        context = MagicMock(spec=[])  # No tracker_dir attribute

        # Mock database exists
        mock_exists.return_value = True

        # Mock successful initialization
        mock_process = MagicMock()
        mock_process.communicate.return_value = ("Success", "")
        mock_process.returncode = 0
        mock_popen.return_value = mock_process

        _reinitialize_database(context)

        # Should use default 'tracker' directory
        call_args = mock_popen.call_args[0][0]
        assert call_args[2] == "tracker"
