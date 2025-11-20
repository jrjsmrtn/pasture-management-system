# SPDX-FileCopyrightText: 2025 Georges Martin <jrjsmrtn@gmail.com>
# SPDX-License-Identifier: MIT

"""Custom actions for Configuration Item (CI) class."""

import csv
from io import StringIO

from roundup.cgi.actions import Action


class ExportCSVAction(Action):
    """Export CI list to CSV format."""

    def handle(self):
        """Handle CSV export request."""
        # Get all CIs (respecting current filters)
        db = self.db
        ci_class = db.ci

        # Get all CI IDs
        ci_ids = ci_class.list()

        # Build CSV in memory
        output = StringIO()
        writer = csv.writer(output)

        # Write header
        writer.writerow(
            [
                "ID",
                "Name",
                "Type",
                "Status",
                "Criticality",
                "Location",
                "IP Address",
                "Description",
            ]
        )

        # Write CI data
        for ci_id in ci_ids:
            ci = ci_class.getnode(ci_id)

            # Get related items with safe lookups
            ci_type = db.citype.get(ci.type, "name") if ci.type else ""
            ci_status = db.cistatus.get(ci.status, "name") if ci.status else ""
            ci_criticality = db.cicriticality.get(ci.criticality, "name") if ci.criticality else ""

            writer.writerow(
                [
                    ci_id,
                    ci.name or "",
                    ci_type,
                    ci_status,
                    ci_criticality,
                    ci.location or "",
                    ci.ip_address or "",
                    ci.description or "",
                ]
            )

        # Set response headers for CSV download
        csv_data = output.getvalue()
        self.client.setHeader("Content-Type", "text/csv; charset=utf-8")
        self.client.setHeader("Content-Disposition", 'attachment; filename="cmdb_export.csv"')
        self.client.setHeader("Content-Length", str(len(csv_data)))

        # Write CSV data to response
        self.client.write(csv_data)

        # Return None to prevent default template rendering
        return None


def init(instance):
    """Register custom actions."""
    instance.registerAction("export_csv", ExportCSVAction)
