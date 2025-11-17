# SPDX-FileCopyrightText: 2025 Georges Martin <jrjsmrtn@gmail.com>
# SPDX-License-Identifier: MIT

"""
Custom actions for CI Relationship creation with proper error handling.

This extends Roundup's NewItemAction to properly display Reject exceptions
from auditor detectors by redirecting back to the form with the error message.
"""

import logging


try:
    import urllib.parse as urllib_
except ImportError:
    import urllib as urllib_

from roundup.cgi import exceptions
from roundup.cgi.actions import NewItemAction
from roundup.exceptions import Reject


logger = logging.getLogger(__name__)


class CIRelationshipNewAction(NewItemAction):
    """Custom new item action for CI relationships that handles validation errors properly."""

    def handle(self):
        """Create a new CI relationship with proper error display on validation failure."""
        # Ensure modification comes via POST
        if self.client.env["REQUEST_METHOD"] != "POST":
            raise Reject(self._("Invalid request"))

        # Parse the props from the form
        try:
            props, links = self.client.parsePropsFromForm(create=1)
        except (ValueError, KeyError) as message:
            self.client.add_error_message(self._("Error: %s") % str(message))
            return

        # Handle the props - edit or create
        try:
            messages = self._editnodes(props, links)
        except (ValueError, KeyError, IndexError, Reject) as message:
            error_msg = str(message)
            logger.warning(f"CI relationship creation failed: {error_msg}")

            # Instead of just returning, redirect back to the form with error
            # Get the source_ci from props to redirect back to the right CI
            source_ci = props.get(("cirelationship", None), {}).get("source_ci")
            if source_ci:
                # Redirect back to the source CI page with error message
                url = f"{self.base}ci{source_ci}?@error_message={urllib_.quote(error_msg)}"
            else:
                # Fallback: redirect to CI list
                url = f"{self.base}ci?@error_message={urllib_.quote(error_msg)}"

            raise exceptions.Redirect(url)

        # Commit now that all the tricky stuff is done
        self.db.commit()

        # Redirect to success page
        # If __redirect_to is specified, use it
        if "__redirect_to" in self.form:
            redirect_url = self.examine_url(self.form["__redirect_to"].value)
            raise exceptions.Redirect(f"{redirect_url}&@ok_message={urllib_.quote(messages)}")

        # Otherwise redirect to the new relationship's page
        raise exceptions.Redirect(
            f"{self.base}{self.classname}{self.nodeid}"
            f"?@ok_message={urllib_.quote(messages)}"
            f"&@template={urllib_.quote(self.template)}"
        )


def init(instance):
    """Register custom actions with the tracker."""
    instance.registerAction("cirelationship_new", CIRelationshipNewAction)
