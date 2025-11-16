<!--
SPDX-FileCopyrightText: 2025 Georges Martin <jrjsmrtn@gmail.com>
SPDX-License-Identifier: MIT
-->

# Sprint 3 Plan - Pasture Management System

**Sprint Duration**: 2 weeks
**Sprint Goal**: Complete change management workflows with approval process
**Target Version**: v0.4.0
**Start Date**: TBD
**End Date**: TBD

## Sprint Objective

Implement complete ITIL-inspired change management workflow with approval stages, change-to-issue relationships, and comprehensive testing across all interfaces. This sprint demonstrates the full power of structured change management for homelab environments.

## User Stories

### Epic: Change Management Workflows

#### Story 1: Change Approval Workflow

**As a** homelab sysadmin
**I want** changes to go through approval stages
**So that** I can prevent unauthorized or risky changes

**Acceptance Criteria**:

- Change statuses: Requested, Assessment, Approved, Rejected, Scheduled, Implementing, Completed, Cancelled
- Valid transitions enforced (similar to issue workflow)
- Approval requires justification/notes
- Rejection requires reason
- Status history tracked

**BDD Scenarios**: (Feature file: `features/change_mgmt/change_workflow.feature`)

```gherkin
@story-1 @web-ui @smoke
Scenario: Approve change request
  Given a change exists with status "Requested"
  When I view the change details
  And I click "Start Assessment"
  Then the change status should be "Assessment"
  When I add assessment notes "Risk: Low, Impact: Minimal"
  And I click "Approve"
  Then the change status should be "Approved"
  And I should see "Change approved successfully"

@story-1 @web-ui @validation
Scenario: Cannot skip assessment stage
  Given a change exists with status "Requested"
  When I view the change details
  Then I should not see "Approve" button
  And I should only see "Start Assessment" button

@story-1 @web-ui
Scenario: Reject change with reason
  Given a change exists with status "Assessment"
  When I view the change details
  And I click "Reject"
  And I enter rejection reason "Conflicts with security policy"
  And I confirm rejection
  Then the change status should be "Rejected"
  And the rejection reason should be recorded

@story-1 @cli
Scenario: Update change status via CLI
  Given a change exists with ID "1" and status "Approved"
  When I run "roundup-client update change 1 status=scheduled notes='Scheduled for Saturday 2 AM'"
  Then the command should succeed
  And change "1" should have status "Scheduled"

@story-1 @api
Scenario: Complete change implementation via API
  Given a change exists with ID "1" and status "Implementing"
  When I PATCH "/api/changes/1" with JSON:
    """
    {
      "status": "completed",
      "completion_notes": "Database upgraded successfully, all tests passed"
    }
    """
  Then the response status should be 200
  And the change status should be "Completed"
  And completion notes should be recorded
```

**Story Points**: 8

______________________________________________________________________

#### Story 2: Link Changes to Issues

**As a** homelab sysadmin
**I want** to link change requests to related issues
**So that** I can track which changes address which problems

**Acceptance Criteria**:

- Change can reference one or more issues
- Issue can be referenced by multiple changes
- Relationship viewable from both change and issue
- Links can be added/removed
- Deleting issue doesn't delete change (orphan handling)

**BDD Scenarios**: (Feature file: `features/change_mgmt/change_issue_links.feature`)

```gherkin
@story-2 @web-ui
Scenario: Link change to existing issue
  Given an issue exists with ID "5" and title "Database performance slow"
  And a change exists with ID "10" and title "Upgrade database"
  When I view change "10" details
  And I click "Link Issue"
  And I select issue "5"
  And I click "Add Link"
  Then change "10" should be linked to issue "5"
  And I should see "Linked to Issue #5: Database performance slow"

@story-2 @web-ui
Scenario: View linked changes from issue
  Given an issue exists with ID "5"
  And changes "10" and "11" are linked to issue "5"
  When I view issue "5" details
  Then I should see "Related Changes" section
  And I should see 2 linked changes
  And I should see change "10" and change "11"

@story-2 @api
Scenario: Create change with issue links via API
  Given an issue exists with ID "5"
  When I POST to "/api/changes" with JSON:
    """
    {
      "title": "Fix network issue",
      "description": "Reconfigure network settings",
      "justification": "Resolve connectivity problems",
      "priority": "high",
      "category": "network",
      "linked_issues": [5]
    }
    """
  Then the response status should be 201
  And the change should be linked to issue "5"

@story-2 @cli
Scenario: Link change to issue via CLI
  Given a change exists with ID "10"
  And an issue exists with ID "5"
  When I run "roundup-client link change 10 issue 5"
  Then the command should succeed
  And change "10" should be linked to issue "5"
```

**Story Points**: 5

______________________________________________________________________

#### Story 3: Change Risk Assessment

**As a** homelab sysadmin
**I want** to document risk level and mitigation for changes
**So that** I can make informed decisions about proceeding

**Acceptance Criteria**:

- Risk levels: Very Low, Low, Medium, High, Very High
- Risk assessment fields: likelihood, impact, mitigation plan
- Risk assessment required before approval
- Risk displayed prominently in change view

**BDD Scenarios**: (Feature file: `features/change_mgmt/change_risk.feature`)

```gherkin
@story-3 @web-ui
Scenario: Add risk assessment to change
  Given a change exists with status "Assessment"
  When I view the change details
  And I click "Add Risk Assessment"
  And I select risk level "Medium"
  And I enter likelihood "Moderate"
  And I enter impact "Service downtime 1-2 hours"
  And I enter mitigation "Perform during maintenance window, have rollback plan"
  And I click "Save Assessment"
  Then the risk assessment should be saved
  And I should see risk level "Medium" badge

@story-3 @web-ui @validation
Scenario: Cannot approve high-risk change without mitigation
  Given a change exists with status "Assessment"
  And the change has risk level "High"
  When I view the change details
  And I click "Approve"
  Then I should see "Mitigation plan required for high-risk changes"
  And the change should remain in "Assessment" status

@story-3 @api
Scenario: Update risk assessment via API
  Given a change exists with ID "1"
  When I PATCH "/api/changes/1/risk" with JSON:
    """
    {
      "risk_level": "low",
      "likelihood": "Low probability",
      "impact": "Minimal impact expected",
      "mitigation": "Standard rollback procedure available"
    }
    """
  Then the response status should be 200
  And the risk assessment should be updated
```

**Story Points**: 5

______________________________________________________________________

#### Story 4: Change Scheduling

**As a** homelab sysadmin
**I want** to schedule approved changes for specific times
**So that** I can plan maintenance windows

**Acceptance Criteria**:

- Scheduled start and end time fields
- Calendar view of scheduled changes (optional for this sprint)
- Notifications for upcoming scheduled changes
- Ability to reschedule

**BDD Scenarios**: (Feature file: `features/change_mgmt/change_scheduling.feature`)

```gherkin
@story-4 @web-ui
Scenario: Schedule approved change
  Given a change exists with status "Approved"
  When I view the change details
  And I click "Schedule"
  And I select date "2025-12-01"
  And I select start time "02:00"
  And I select end time "04:00"
  And I click "Save Schedule"
  Then the change status should be "Scheduled"
  And the scheduled time should be "2025-12-01 02:00 - 04:00"

@story-4 @web-ui
Scenario: Reschedule change
  Given a change exists with status "Scheduled" for "2025-12-01 02:00"
  When I view the change details
  And I click "Reschedule"
  And I select date "2025-12-08"
  And I click "Update Schedule"
  Then the scheduled time should be updated
  And the schedule change should be recorded in history

@story-4 @api
Scenario: Schedule change via API
  Given a change exists with ID "1" and status "Approved"
  When I PATCH "/api/changes/1/schedule" with JSON:
    """
    {
      "scheduled_start": "2025-12-01T02:00:00Z",
      "scheduled_end": "2025-12-01T04:00:00Z"
    }
    """
  Then the response status should be 200
  And the change should be scheduled
```

**Story Points**: 5

______________________________________________________________________

#### Story 5: Change Implementation Tracking

**As a** homelab sysadmin
**I want** to track change implementation progress
**So that** I can document what was actually done

**Acceptance Criteria**:

- Implementation notes field
- Actual start/end time tracking
- Deviation from plan documentation
- Success/failure indicators
- Rollback documentation if needed

**BDD Scenarios**: (Feature file: `features/change_mgmt/change_implementation.feature`)

```gherkin
@story-5 @web-ui
Scenario: Begin change implementation
  Given a change exists with status "Scheduled"
  And the scheduled time has arrived
  When I view the change details
  And I click "Start Implementation"
  Then the change status should be "Implementing"
  And the actual start time should be recorded

@story-5 @web-ui
Scenario: Complete change with notes
  Given a change exists with status "Implementing"
  When I view the change details
  And I enter implementation notes "Upgraded database from v15 to v16. Migration took 45 minutes. All tests passed."
  And I click "Mark Complete"
  Then the change status should be "Completed"
  And the actual end time should be recorded
  And implementation notes should be saved

@story-5 @web-ui
Scenario: Document change rollback
  Given a change exists with status "Implementing"
  When I view the change details
  And I click "Rollback"
  And I enter rollback reason "Migration failed validation tests"
  And I enter rollback notes "Restored from backup, downtime was 30 minutes"
  And I confirm rollback
  Then the change status should be "Cancelled"
  And rollback should be documented
```

**Story Points**: 5

______________________________________________________________________

## Technical Tasks

### Change Workflow

- [ ] Define complete status transition matrix
- [ ] Implement workflow validation logic
- [ ] Add approval/rejection functionality
- [ ] Create workflow action buttons in UI
- [ ] Add CLI commands for workflow actions
- [ ] Add API endpoints for status transitions

### Change-Issue Relationships

- [ ] Design relationship schema
- [ ] Implement linking functionality
- [ ] Display relationships in UI
- [ ] Add CLI linking commands
- [ ] Add API linking endpoints

### Risk Assessment

- [ ] Add risk assessment fields to schema
- [ ] Implement risk validation rules
- [ ] Create risk assessment UI
- [ ] Add risk indicators to change list

### Scheduling

- [ ] Add scheduling fields to schema
- [ ] Implement scheduling UI
- [ ] Add time validation
- [ ] Track actual vs. scheduled times

### Implementation Tracking

- [ ] Add implementation fields
- [ ] Create implementation notes UI
- [ ] Track rollback scenarios
- [ ] Document deviations

### Documentation

- [ ] Tutorial: "Managing Changes in Your Homelab"
- [ ] How-to: "Submitting a Change Request"
- [ ] How-to: "Assessing Change Risk"
- [ ] Reference: "Change Workflow States"
- [ ] Explanation: "ITIL Change Management Principles"
- [ ] Marpit presentation: "BDD Testing in Practice"

## Definition of Done

- [ ] All user stories completed with acceptance criteria met
- [ ] All BDD scenarios implemented and passing
- [ ] Change workflow complete with approvals
- [ ] Change-issue linking functional
- [ ] Risk assessment integrated
- [ ] Code passes pre-commit hooks
- [ ] Documentation and presentation completed
- [ ] Test coverage >85%
- [ ] CHANGELOG.md updated for v0.4.0
- [ ] Sprint retrospective completed

## Sprint Backlog

| Task                                    | Story Points | Status      |
| --------------------------------------- | ------------ | ----------- |
| Story 1: Change Approval Workflow       | 8            | ✅ Complete |
| Story 2: Link Changes to Issues         | 5            | ✅ Complete |
| Story 3: Change Risk Assessment         | 5            | ✅ Complete |
| Story 4: Change Scheduling              | 5            | ✅ Complete |
| Story 5: Change Implementation Tracking | 5            | Not Started |
| Documentation and Presentation          | 5            | Not Started |

**Total Story Points**: 33
**Completed**: 23 points (70%)
**In Progress**: 0 points
**Remaining**: 10 points

## Risks and Dependencies

### Risks

- **Workflow Complexity**: Complete change workflow may be more complex than anticipated
  - *Mitigation*: Break down into smaller iterations, test thoroughly
- **UI Complexity**: Multiple workflow actions may clutter interface
  - *Mitigation*: Progressive disclosure, context-sensitive actions

### Dependencies

- Sprint 2 completion (change foundation established)
- Understanding of ITIL change management principles

## Success Metrics

- [ ] Complete change workflow functional end-to-end
- [ ] Change-issue relationships working correctly
- [ ] Risk assessment integrated and validated
- [ ] Minimum 20 BDD scenarios passing
- [ ] Marpit presentation demonstrates BDD value
- [ ] Sprint goal achieved: full change management capability
