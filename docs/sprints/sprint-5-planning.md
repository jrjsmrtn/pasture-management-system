<!--
SPDX-FileCopyrightText: 2025 Georges Martin <jrjsmrtn@gmail.com>
SPDX-License-Identifier: MIT
-->

# Sprint 5 Plan - Pasture Management System

**Sprint Duration**: 2 weeks
**Sprint Goal**: Add reporting, dashboards, and analytics capabilities
**Target Version**: v0.6.0
**Start Date**: TBD
**End Date**: TBD

## Sprint Objective

Implement reporting and dashboard capabilities to provide visibility into homelab operations. Add metrics, analytics, and visualization to help sysadmins understand their issue trends, change success rates, and CMDB health. This sprint focuses on operational insights and management visibility.

## User Stories

### Epic: Reporting and Dashboards

#### Story 1: Issue Statistics Dashboard
**As a** homelab sysadmin
**I want** to see issue statistics at a glance
**So that** I can understand my homelab's health

**Acceptance Criteria**:
- Dashboard shows: total issues, open issues, resolved issues, average resolution time
- Issue trend chart (last 30 days)
- Issues by priority breakdown
- Issues by assignee
- Top 10 most common issue types
- Auto-refresh capability

**BDD Scenarios**: (Feature file: `features/reporting/issue_dashboard.feature`)
```gherkin
@story-1 @web-ui @smoke
Scenario: View issue statistics dashboard
  Given I am logged in to the web UI
  And the following issues exist:
    | title    | status   | priority | created_date |
    | Issue 1  | Open     | High     | 2025-11-01   |
    | Issue 2  | Resolved | Medium   | 2025-11-05   |
    | Issue 3  | Open     | Low      | 2025-11-10   |
    | Issue 4  | Resolved | High     | 2025-11-12   |
  When I navigate to "Dashboard"
  Then I should see "Total Issues: 4"
  And I should see "Open Issues: 2"
  And I should see "Resolved Issues: 2"
  And I should see priority breakdown chart
  And I should see issue trend chart

@story-1 @web-ui
Scenario: View average resolution time
  Given the following resolved issues exist:
    | title   | created_date | resolved_date |
    | Issue 1 | 2025-11-01   | 2025-11-03    |
    | Issue 2 | 2025-11-05   | 2025-11-06    |
  When I navigate to "Dashboard"
  Then I should see "Average Resolution Time: 1.5 days"

@story-1 @api
Scenario: Fetch issue statistics via API
  Given I have a valid API token
  When I GET "/api/reports/issue-stats"
  Then the response status should be 200
  And the response should include:
    """
    {
      "total": 4,
      "open": 2,
      "resolved": 2,
      "avg_resolution_days": 1.5,
      "by_priority": {
        "high": 2,
        "medium": 1,
        "low": 1
      }
    }
    """
```

**Story Points**: 8

---

#### Story 2: Change Management Reports
**As a** homelab sysadmin
**I want** to see change success rates and metrics
**So that** I can improve my change management process

**Acceptance Criteria**:
- Total changes, approved, rejected, completed
- Change success rate (completed without rollback)
- Average change duration
- Changes by category
- Scheduled vs. emergency changes ratio
- Risk level distribution

**BDD Scenarios**: (Feature file: `features/reporting/change_reports.feature`)
```gherkin
@story-2 @web-ui
Scenario: View change management metrics
  Given the following changes exist:
    | title    | status    | category | risk   |
    | Change 1 | Completed | Software | Low    |
    | Change 2 | Completed | Hardware | Medium |
    | Change 3 | Rejected  | Network  | High   |
    | Change 4 | Completed | Software | Low    |
  When I navigate to "Reports" > "Change Management"
  Then I should see "Total Changes: 4"
  And I should see "Completed: 3"
  And I should see "Rejected: 1"
  And I should see "Success Rate: 75%"
  And I should see category breakdown chart

@story-2 @web-ui
Scenario: View change risk analysis
  Given the following changes exist:
    | title    | risk   | status    |
    | Change 1 | Low    | Completed |
    | Change 2 | Medium | Completed |
    | Change 3 | High   | Rejected  |
    | Change 4 | Low    | Completed |
  When I navigate to "Reports" > "Change Risk Analysis"
  Then I should see risk distribution:
    | risk   | count | percentage |
    | Low    | 2     | 50%        |
    | Medium | 1     | 25%        |
    | High   | 1     | 25%        |

@story-2 @api
Scenario: Export change metrics via API
  Given I have a valid API token
  When I GET "/api/reports/change-metrics?period=last_30_days"
  Then the response status should be 200
  And the response should include change statistics
```

**Story Points**: 5

---

#### Story 3: CMDB Health Report
**As a** homelab sysadmin
**I want** to see CMDB health and coverage
**So that** I can ensure my infrastructure is properly documented

**Acceptance Criteria**:
- Total CIs by type
- CI status distribution (Active, Maintenance, Retired)
- CIs by criticality
- Orphaned CIs (no relationships)
- Incomplete CI records (missing critical attributes)
- CI relationship coverage

**BDD Scenarios**: (Feature file: `features/reporting/cmdb_reports.feature`)
```gherkin
@story-3 @web-ui
Scenario: View CMDB health dashboard
  Given the following CIs exist:
    | name      | type   | status | criticality |
    | Server 1  | Server | Active | High        |
    | Server 2  | Server | Active | Medium      |
    | Switch 1  | Network| Active | High        |
    | Old Box   | Server | Retired| Low         |
  When I navigate to "Reports" > "CMDB Health"
  Then I should see "Total CIs: 4"
  And I should see "Active CIs: 3"
  And I should see CI type breakdown:
    | type    | count |
    | Server  | 3     |
    | Network | 1     |
  And I should see criticality breakdown

@story-3 @web-ui
Scenario: Identify orphaned CIs
  Given CI "server-01" has 2 relationships
  And CI "old-server" has 0 relationships
  And CI "switch-01" has 5 relationships
  When I navigate to "Reports" > "CMDB Health"
  And I view "Orphaned CIs" section
  Then I should see 1 orphaned CI
  And I should see "old-server" in orphaned list

@story-3 @web-ui
Scenario: Identify incomplete CI records
  Given CI "server-01" has all required attributes
  And CI "server-02" is missing IP address
  And CI "server-03" is missing criticality
  When I navigate to "Reports" > "CMDB Health"
  And I view "Data Quality" section
  Then I should see "2 CIs with incomplete data"
  And I should see recommendations to complete records

@story-3 @api
Scenario: Get CMDB health metrics via API
  Given I have a valid API token
  When I GET "/api/reports/cmdb-health"
  Then the response status should be 200
  And the response should include CI statistics
  And the response should include data quality metrics
```

**Story Points**: 5

---

#### Story 4: Custom Report Builder
**As a** homelab sysadmin
**I want** to create custom reports
**So that** I can analyze specific aspects of my homelab

**Acceptance Criteria**:
- Select entity type (Issue, Change, CI)
- Choose fields to display
- Apply filters (date range, status, priority, etc.)
- Sort and group results
- Export to CSV, JSON, PDF
- Save report templates

**BDD Scenarios**: (Feature file: `features/reporting/custom_reports.feature`)
```gherkin
@story-4 @web-ui
Scenario: Create custom issue report
  Given I am logged in to the web UI
  When I navigate to "Reports" > "Custom Reports"
  And I click "New Report"
  And I select entity type "Issue"
  And I select fields "Title, Priority, Status, Created Date"
  And I filter by "Status = Open"
  And I filter by "Priority = High"
  And I sort by "Created Date" descending
  And I click "Generate Report"
  Then I should see a report with high-priority open issues
  And the report should be sorted by creation date

@story-4 @web-ui
Scenario: Save and reuse report template
  Given I have created a custom report
  When I click "Save Template"
  And I enter template name "Weekly High Priority Issues"
  And I click "Save"
  Then the template should be saved
  When I navigate to "Reports" > "Saved Templates"
  Then I should see "Weekly High Priority Issues"
  When I click "Weekly High Priority Issues"
  Then the report should be generated with saved parameters

@story-4 @web-ui
Scenario: Export report to CSV
  Given I have generated a custom report
  When I click "Export"
  And I select format "CSV"
  Then a CSV file should be downloaded
  And the CSV should contain the report data

@story-4 @api
Scenario: Generate custom report via API
  Given I have a valid API token
  When I POST to "/api/reports/custom" with JSON:
    """
    {
      "entity": "issue",
      "fields": ["title", "priority", "status"],
      "filters": {
        "status": "open",
        "priority": "high"
      },
      "sort": {"field": "created_date", "order": "desc"}
    }
    """
  Then the response status should be 200
  And the response should include filtered and sorted issues
```

**Story Points**: 8

---

#### Story 5: Email/Scheduled Reports
**As a** homelab sysadmin
**I want** to receive scheduled reports via email
**So that** I can stay informed without logging in

**Acceptance Criteria**:
- Schedule reports (daily, weekly, monthly)
- Email delivery configuration
- PDF attachment format
- Summary in email body
- Enable/disable scheduled reports
- Report delivery history

**BDD Scenarios**: (Feature file: `features/reporting/scheduled_reports.feature`)
```gherkin
@story-5 @web-ui
Scenario: Schedule weekly report
  Given I am logged in to the web UI
  When I navigate to "Reports" > "Scheduled Reports"
  And I click "New Scheduled Report"
  And I select report type "Issue Summary"
  And I select frequency "Weekly"
  And I select day "Monday"
  And I select time "09:00"
  And I enter email "admin@homelab.local"
  And I click "Schedule"
  Then the report should be scheduled
  And I should see "Report scheduled successfully"

@story-5 @web-ui
Scenario: View scheduled report history
  Given a scheduled report has been sent 3 times
  When I navigate to "Reports" > "Scheduled Reports"
  And I click on the scheduled report
  And I view "Delivery History"
  Then I should see 3 delivery records
  And each record should show timestamp and status

@story-5 @cli
Scenario: Trigger scheduled report manually
  Given a scheduled report exists with ID "1"
  When I run "roundup-client report send 1"
  Then the command should succeed
  And the report should be sent immediately
  And I should see "Report sent successfully"

@story-5 @api
Scenario: Create scheduled report via API
  Given I have a valid API token
  When I POST to "/api/reports/scheduled" with JSON:
    """
    {
      "report_type": "change_summary",
      "frequency": "monthly",
      "day_of_month": 1,
      "time": "08:00",
      "email": "admin@homelab.local",
      "format": "pdf"
    }
    """
  Then the response status should be 201
  And the scheduled report should be created
```

**Story Points**: 8

---

## Technical Tasks

### Dashboard Infrastructure
- [ ] Create dashboard framework
- [ ] Implement charting library integration
- [ ] Add real-time data refresh
- [ ] Create responsive dashboard layouts

### Issue Reporting
- [ ] Calculate issue statistics
- [ ] Generate issue trend data
- [ ] Create issue visualizations
- [ ] Implement resolution time calculations

### Change Reporting
- [ ] Calculate change metrics
- [ ] Generate success rate analytics
- [ ] Create change category breakdown
- [ ] Implement risk analysis reports

### CMDB Reporting
- [ ] Calculate CMDB health metrics
- [ ] Identify orphaned CIs
- [ ] Detect incomplete records
- [ ] Generate CI coverage reports

### Custom Reports
- [ ] Implement report builder UI
- [ ] Add field selection logic
- [ ] Implement dynamic filtering
- [ ] Add export functionality (CSV, JSON, PDF)
- [ ] Create report template storage

### Scheduled Reports
- [ ] Implement report scheduling
- [ ] Add email delivery (SMTP configuration)
- [ ] Generate PDF reports
- [ ] Track delivery history
- [ ] Add manual trigger capability

### Documentation
- [ ] How-to: "Generating Reports"
- [ ] How-to: "Creating Custom Reports"
- [ ] How-to: "Scheduling Automated Reports"
- [ ] Reference: "Available Metrics and KPIs"
- [ ] Tutorial: "Understanding Your Homelab Metrics"

## Definition of Done

- [ ] All user stories completed with acceptance criteria met
- [ ] All BDD scenarios implemented and passing
- [ ] Dashboards functional with real-time data
- [ ] Custom report builder operational
- [ ] Scheduled reports working with email delivery
- [ ] Code passes pre-commit hooks
- [ ] Documentation completed
- [ ] Test coverage >85%
- [ ] Screenshots at 1024x768 for all dashboard views
- [ ] CHANGELOG.md updated for v0.6.0
- [ ] Sprint retrospective completed

## Sprint Backlog

| Task | Story Points | Status |
|------|-------------|--------|
| Story 1: Issue Statistics Dashboard | 8 | Not Started |
| Story 2: Change Management Reports | 5 | Not Started |
| Story 3: CMDB Health Report | 5 | Not Started |
| Story 4: Custom Report Builder | 8 | Not Started |
| Story 5: Email/Scheduled Reports | 8 | Not Started |
| Documentation Tasks | 5 | Not Started |

**Total Story Points**: 39

## Risks and Dependencies

### Risks
- **Email Configuration Complexity**: SMTP setup can be environment-specific
  - *Mitigation*: Support multiple email backends, provide clear documentation
- **Report Performance**: Large datasets may impact report generation time
  - *Mitigation*: Implement caching, optimize queries, add pagination

### Dependencies
- Sprint 4 completion (CMDB functional)
- Charting library selection (e.g., Chart.js, D3.js)
- Email server configuration for homelab

## Success Metrics

- [ ] Dashboard loads in <2 seconds
- [ ] Custom reports generate in <5 seconds
- [ ] Scheduled reports deliver reliably
- [ ] Minimum 30 BDD scenarios passing
- [ ] All visualizations render correctly at 1024x768
- [ ] Sprint goal achieved: Full operational visibility
