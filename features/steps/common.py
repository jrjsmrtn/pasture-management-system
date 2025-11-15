# SPDX-FileCopyrightText: 2025 Georges Martin <jrjsmrtn@gmail.com>
# SPDX-License-Identifier: MIT

"""Common constants and utilities for BDD step definitions."""

# Priority mapping (label -> Roundup ID)
# Used across Web UI, CLI, and REST API interfaces
PRIORITY_MAP = {
    "critical": "1",
    "urgent": "2",
    "bug": "3",
    "feature": "4",
    "wish": "5",
}
