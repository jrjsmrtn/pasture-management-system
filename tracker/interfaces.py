# SPDX-FileCopyrightText: 2025 Georges Martin <jrjsmrtn@gmail.com>
# SPDX-License-Identifier: MIT

"""Roundup tracker interfaces - registers custom actions and extensions."""


def init(instance):
    """Initialize custom actions and extensions for this tracker.

    This function is called by Roundup when the tracker is initialized.
    It registers custom actions defined in the extensions directory.
    """
    # Register CI-related custom actions
    from extensions import ci_actions

    ci_actions.init(instance)

    # Register CI relationship custom actions
    from extensions import cirelationship_actions

    cirelationship_actions.init(instance)
