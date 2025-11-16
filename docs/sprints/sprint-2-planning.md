<!--
SPDX-FileCopyrightText: 2025 Georges Martin <jrjsmrtn@gmail.com>
SPDX-License-Identifier: MIT
-->

# Sprint 2 Plan - Pasture Management System

**Sprint Duration**: 2 weeks
**Sprint Goal**: Implement issue lifecycle workflow and introduce change management foundation
**Target Version**: v0.3.0
**Start Date**: 2025-11-15
**End Date**: 2025-11-29

## Sprint Objective

Implement issue status transitions following ITIL-inspired workflow patterns and establish the foundation for change management. This sprint introduces workflow automation and begins demonstrating ITIL concepts to homelab sysadmins.

## User Stories

### Epic: Issue Lifecycle Management

#### Story 1: Issue Status Workflow

**As a** homelab sysadmin
**I want** issues to move through defined statuses
**So that** I can track progress on resolving problems

**Acceptance Criteria**:

- Issue statuses: New, In Progress, Resolved, Closed
- Valid transitions defined (e.g., New → In Progress, not New → Closed)
- Status changes recorded with timestamp
- Status history viewable
- Invalid transitions rejected with error message

**BDD Scenarios**: (Feature file: `features/issue_tracking/issue_workflow.feature`)

```gherkin
@story-1 @web-ui @smoke
Scenario: Transition issue from New to In Progress
  Given an issue exists with status "New"
  When I view the issue details
  And I click "Start Work"
  Then the issue status should be "In Progress"
  And I should see "Status updated successfully"
  And the status change should be recorded in history

@story-1 @web-ui @validation
Scenario: Cannot transition from New to Closed directly
  Given an issue exists with status "New"
  When I view the issue details
  Then I should not see "Close Issue" button
  And only valid transitions should be available

@story-1 @cli
Scenario: Update issue status via CLI
  Given an issue exists with ID "1" and status "New"
  When I run "roundup-client update issue 1 status=in_progress"
  Then the command should succeed
  And issue "1" should have status "In Progress"

@story-1 @api
Scenario: Transition issue via API
  Given an issue exists with ID "1" and status "In Progress"
  When I PATCH "/api/issues/1" with JSON:
    """
    {
      "status": "resolved"
    }
    """
  Then the response status should be 200
  And the issue status should be "Resolved"
```

**Story Points**: 8

______________________________________________________________________

#### Story 2: Assign Issues to Owner

**As a** homelab sysadmin
**I want** to assign issues to specific people
**So that** responsibilities are clear

**Acceptance Criteria**:

- Issue has assignee field
- User list available for assignment
- Assignee can be set during creation or later
- Assignee can be changed
- Filter issues by assignee

**BDD Scenarios**: (Feature file: `features/issue_tracking/assign_issues.feature`)

```gherkin
@story-2 @web-ui
Scenario: Assign issue to user
  Given I am logged in as "admin"
  And an issue exists with title "Network issue"
  When I view the issue details
  And I select assignee "jdoe"
  And I click "Save"
  Then the issue should be assigned to "jdoe"

@story-2 @web-ui
Scenario: Filter issues by assignee
  Given the following issues exist:
    | title        | assignee |
    | Issue 1      | jdoe     |
    | Issue 2      | jsmith   |
    | Issue 3      | jdoe     |
  When I navigate to "Issues"
  And I filter by assignee "jdoe"
  Then I should see 2 issues
  And I should see "Issue 1" and "Issue 3"
```

**Story Points**: 3

______________________________________________________________________

### Epic: Change Management Foundation

#### Story 3: Define Change Request Schema

**As a** homelab sysadmin
**I want** to track change requests separately from issues
**So that** I can manage planned changes systematically

**Acceptance Criteria**:

- Change schema defined with fields: title, description, justification, impact, risk
- Change priority levels: Low, Medium, High, Critical
- Change categories: Software, Hardware, Configuration, Network
- Schema documented in reference docs
- Database migration successful

**BDD Scenarios**: (Feature file: `features/change_mgmt/change_schema.feature`)

```gherkin
@story-3 @api
Scenario: Verify change schema fields
  Given I have a valid API token
  When I GET "/api/schema/change"
  Then the response should include fields:
    | field         | type   | required |
    | title         | string | true     |
    | description   | text   | true     |
    | justification | text   | true     |
    | impact        | text   | false    |
    | risk          | string | false    |
    | priority      | string | true     |
    | category      | string | true     |
```

**Story Points**: 3

______________________________________________________________________

#### Story 4: Create Change Request

**As a** homelab sysadmin
**I want** to create change requests
**So that** I can plan and track infrastructure changes

**Acceptance Criteria**:

- Web UI form for change creation
- Required fields validated
- Change saved to database
- Success confirmation displayed
- Change viewable in change list

**BDD Scenarios**: (Feature file: `features/change_mgmt/create_change.feature`)

```gherkin
@story-4 @web-ui @smoke
Scenario: Create change request with required fields
  Given I am logged in to the web UI
  When I navigate to "New Change"
  And I enter title "Upgrade database to PostgreSQL 16"
  And I enter description "Upgrade from PostgreSQL 15 to 16 for performance improvements"
  And I enter justification "Better query performance and new features"
  And I select priority "Medium"
  And I select category "Software"
  And I click "Submit"
  Then I should see "Change request created successfully"
  And the change should appear in the change list

@story-4 @web-ui @validation
Scenario: Cannot create change without justification
  Given I am logged in to the web UI
  When I navigate to "New Change"
  And I enter title "Some change"
  And I enter description "Description"
  And I click "Submit"
  Then I should see "Justification is required"

@story-4 @cli
Scenario: Create change via CLI
  When I run "roundup-client create change title='Firewall update' description='Update firewall rules' justification='Security improvement' priority=high category=configuration"
  Then the command should succeed
  And I should see "Change created: #1"

@story-4 @api
Scenario: Create change via API
  Given I have a valid API token
  When I POST to "/api/changes" with JSON:
    """
    {
      "title": "Backup schedule modification",
      "description": "Change backup time to 2 AM",
      "justification": "Reduce impact on production systems",
      "priority": "low",
      "category": "configuration"
    }
    """
  Then the response status should be 201
  And the change should exist in the database
```

**Story Points**: 5

______________________________________________________________________

#### Story 5: View Change List

**As a** homelab sysadmin
**I want** to see all change requests
**So that** I can track planned infrastructure changes

**Acceptance Criteria**:

- Web UI displays change list
- Changes sorted by priority and creation date
- Filter by status, priority, category
- Click change to view details

**BDD Scenarios**: (Feature file: `features/change_mgmt/view_changes.feature`)

```gherkin
@story-5 @web-ui
Scenario: View list of changes
  Given the following changes exist:
    | title              | priority | category      |
    | Database upgrade   | High     | Software      |
    | Network reconfig   | Medium   | Network       |
    | Add disk space     | Low      | Hardware      |
  When I navigate to "Changes"
  Then I should see 3 changes
  And "Database upgrade" should appear before "Network reconfig"

@story-5 @web-ui
Scenario: Filter changes by category
  Given the following changes exist:
    | title              | category      |
    | Database upgrade   | Software      |
    | Network reconfig   | Network       |
    | Add disk space     | Hardware      |
  When I navigate to "Changes"
  And I filter by category "Software"
  Then I should see 1 change
  And I should see "Database upgrade"
```

**Story Points**: 3

______________________________________________________________________

## Technical Tasks

### Issue Workflow

- [ ] Define status transition matrix
- [ ] Implement status validation logic
- [ ] Add status history tracking
- [ ] Update web UI templates for workflow actions
- [ ] Add CLI commands for status updates
- [ ] Add API endpoints for status transitions

### User Assignment

- [ ] Add assignee field to issue schema
- [ ] Create user management basics
- [ ] Implement assignment web UI
- [ ] Add filtering by assignee

### Change Management

- [ ] Design change request schema
- [ ] Create database migration
- [ ] Implement change creation (web/CLI/API)
- [ ] Create change list views
- [ ] Add filtering and sorting

### Documentation

- [ ] Tutorial: "Understanding ITIL Workflows"
- [ ] How-to: "Managing Issue Lifecycle"
- [ ] Reference: "Issue Status Transitions"
- [ ] Reference: "Change Request Schema"
- [ ] Explanation: "Why Change Management Matters"

## Definition of Done

- [ ] All user stories completed with acceptance criteria met
- [ ] All BDD scenarios implemented and passing
- [ ] Issue workflow enforces valid transitions
- [ ] Change management schema documented
- [ ] Code passes pre-commit hooks
- [ ] Tutorial published
- [ ] Test coverage >85%
- [ ] CHANGELOG.md updated for v0.3.0
- [ ] Sprint retrospective completed

## Sprint Backlog

| Task                                  | Story Points | Status      |
| ------------------------------------- | ------------ | ----------- |
| Story 1: Issue Status Workflow        | 8            | Not Started |
| Story 2: Assign Issues to Owner       | 3            | Not Started |
| Story 3: Define Change Request Schema | 3            | Not Started |
| Story 4: Create Change Request        | 5            | Not Started |
| Story 5: View Change List             | 3            | Not Started |
| Documentation Tasks                   | 5            | Not Started |

**Total Story Points**: 27

## Risks and Dependencies

### Risks

- **Workflow Complexity**: Status transitions may be more complex than anticipated
  - *Mitigation*: Start with simple linear workflow, iterate based on feedback
- **Schema Migration**: Database changes need careful testing
  - *Mitigation*: Test migrations on separate database copy first

### Dependencies

- Sprint 1 completion (basic issue tracking functional)
- Roundup detector/reactor customization knowledge

## Success Metrics

- [ ] All issue status transitions validated correctly
- [ ] Change request creation functional across all interfaces
- [ ] Minimum 15 BDD scenarios passing
- [ ] Tutorial explains ITIL concepts clearly
- [ ] Sprint goal achieved: workflow automation and change foundation
