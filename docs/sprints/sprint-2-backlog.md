<!--
SPDX-FileCopyrightText: 2025 Georges Martin <jrjsmrtn@gmail.com>
SPDX-License-Identifier: MIT
-->

# Sprint 2 Backlog - Pasture Management System

**Sprint**: 2 (Issue Lifecycle & Change Management Foundation)
**Target Version**: v0.3.0
**Status**: 🔄 In Progress
**Start Date**: 2025-11-15
**End Date**: 2025-11-29

## Sprint Goal

Implement issue status transitions following ITIL-inspired workflow patterns and establish the foundation for change management.

## Story Points Summary

- **Total Story Points**: 27
- **Completed**: 14 (Stories 1-3)
- **In Progress**: 0
- **Remaining**: 13

## Backlog Items

### Epic: Issue Lifecycle Management

#### Story 1: Issue Status Workflow
**Story Points**: 8
**Priority**: Critical
**Status**: ✅ Complete
**Assignee**: Claude

**User Story**:
> As a homelab sysadmin, I want issues to move through defined statuses so that I can track progress on resolving problems.

**Acceptance Criteria**:
- [x] Issue statuses: New, In Progress, Resolved, Closed
- [x] Valid transitions defined (e.g., New → In Progress, not New → Closed)
- [x] Status changes recorded with timestamp
- [x] Status history viewable
- [x] Invalid transitions rejected with error message

**BDD Scenarios**: 7 scenarios - **ALL PASSING** ✅
1. ✅ Transition issue from New to In Progress (@web-ui @smoke)
2. ✅ Cannot transition from New to Closed directly (@web-ui @validation)
3. ✅ Update issue status via CLI (@cli)
4. ✅ Transition issue via API (@api)
5. ✅ View status history
6. ✅ Complete workflow from New to Closed
7. ✅ Invalid status transition is rejected (API validation)

**Technical Tasks**:
- [x] Define status values (new, in-progress, resolved, closed)
- [x] Implement status validation detector
- [x] Add status history tracking (audit trail)
- [x] Update web UI templates with workflow buttons
- [x] Add CLI commands for status updates
- [x] Add API PATCH endpoint for status transitions
- [x] Create feature file: `features/issue_tracking/issue_workflow.feature`
- [x] Implement step definitions: `features/steps/workflow_steps.py`
- [x] Write BDD scenarios (7 scenarios)
- [x] Verify all scenarios passing

**Completion Notes**:
- 2025-11-15: Created comprehensive BDD feature file with 7 scenarios
- 2025-11-15: Updated initial_data.py with ITIL workflow statuses
- 2025-11-15: Reinitialized tracker database with new status values
- 2025-11-15: Implemented complete workflow step definitions (305 lines)
- 2025-11-15: Created status validation detector with ITIL rules
- 2025-11-15: Added context-sensitive workflow buttons to Web UI
- 2025-11-15: **All 7 scenarios passing** (48 steps, 0 failures)
- 2025-11-15: Committed and pushed (commit f4628e4)

**Files to Create/Modify**:
- `features/issue_tracking/issue_workflow.feature`
- `features/steps/workflow_steps.py`
- `tracker/detectors/status_workflow.py`
- `tracker/schema.py` (add status history)
- `tracker/html/issue.item.html` (workflow buttons)

**Dependencies**: None (builds on Sprint 1)

---

#### Story 2: Assign Issues to Owner
**Story Points**: 3
**Priority**: High
**Status**: ✅ Complete
**Assignee**: Claude

**User Story**:
> As a homelab sysadmin, I want to assign issues to specific people so that responsibilities are clear.

**Acceptance Criteria**:
- [x] Issue has assignee field
- [x] User list available for assignment
- [x] Assignee can be set during creation or later
- [x] Assignee can be changed
- [x] Filter issues by assignee

**BDD Scenarios**: 4 scenarios - **ALL PASSING** ✅
1. ✅ Assign issue to user during creation (@web-ui @smoke)
2. ✅ Change issue assignee (@web-ui)
3. ✅ Filter issues by assignee (@web-ui)
4. ✅ View unassigned issues (@web-ui)

**Technical Tasks**:
- [x] Assignee field already exists in schema (Link to user)
- [x] Assignee dropdown already in UI (issue.item.html line 88-89)
- [x] Filter functionality already exists (issue.index.html sort/group)
- [x] Create feature file: `features/issue_tracking/assign_issues.feature`
- [x] Implement step definitions: `features/steps/assignment_steps.py`
- [x] Update view_steps.py to support assignedto field
- [x] Write BDD scenarios (4 scenarios)
- [x] Verify all scenarios passing

**Completion Notes**:
- 2025-11-15: Created BDD feature file with 4 scenarios
- 2025-11-15: Implemented assignment step definitions (103 lines)
- 2025-11-15: Updated view_steps.py to support assignedto in issue creation
- 2025-11-15: Fixed priority validation issue (Roundup requires priority)
- 2025-11-15: Simplified scenario 1 to use CLI creation + Web UI assignment
- 2025-11-15: **All 4 scenarios passing** (32 steps, 0 failures)

**Files to Create/Modify**:
- `features/issue_tracking/assign_issues.feature` ✅
- `features/steps/assignment_steps.py` ✅
- `features/steps/view_steps.py` ✅ (updated)
- `tracker/schema.py` (assignee field already exists)
- `tracker/html/issue.item.html` (assignee dropdown already exists)
- `tracker/html/issue.index.html` (filter already exists)

**Dependencies**: None

---

### Epic: Change Management Foundation

#### Story 3: Define Change Request Schema
**Story Points**: 3
**Priority**: High
**Status**: ✅ Complete
**Assignee**: Claude

**User Story**:
> As a homelab sysadmin, I want to track change requests separately from issues so that I can manage planned changes systematically.

**Acceptance Criteria**:
- [x] Change schema defined with fields: title, description, justification, impact, risk
- [x] Change priority levels: Low, Medium, High, Critical
- [x] Change categories: Software, Hardware, Configuration, Network
- [x] Change statuses: Proposed, Approved, Scheduled, Implemented, Closed
- [x] Database reinitialized successfully

**BDD Scenarios**: 4 scenarios - **ALL PASSING** ✅
1. ✅ Verify change schema fields via API (@api)
2. ✅ Verify change priorities exist (@api)
3. ✅ Verify change categories exist (@api)
4. ✅ Verify change statuses exist (@api)

**Technical Tasks**:
- [x] Design change request schema (ITIL-based)
- [x] Add Change class to schema.py (IssueClass with custom fields)
- [x] Add changepriority, changecategory, changestatus classes
- [x] Define change properties (description, justification, impact, risk, assignedto, related_issues)
- [x] Create initial_data for change priorities (4), categories (4), statuses (5)
- [x] Reinitialize database with new schema
- [x] Create feature file: `features/change_mgmt/change_schema.feature`
- [x] Implement step definitions: `features/steps/change_schema_steps.py`
- [x] Write API tests for schema verification (4 scenarios)
- [x] Verify all scenarios passing

**Completion Notes**:
- 2025-11-15: Designed Change class extending IssueClass (inherits title, messages, files, nosy)
- 2025-11-15: Added changepriority (low/medium/high/critical), changecategory (software/hardware/configuration/network), changestatus (proposed→approved→scheduled→implemented→closed)
- 2025-11-15: Created BDD feature file with 4 API verification scenarios
- 2025-11-15: Implemented API step definitions with detail fetching for name verification
- 2025-11-15: Reinitialized database successfully
- 2025-11-15: **All 4 scenarios passing** (30 steps, 0 failures)

**Files to Create/Modify**:
- `features/change_mgmt/change_schema.feature` ✅
- `features/steps/change_schema_steps.py` ✅
- `tracker/schema.py` ✅ (Change class + supporting classes)
- `tracker/initial_data.py` ✅ (priorities, categories, statuses)

**Dependencies**: None

---

#### Story 4: Create Change Request
**Story Points**: 5
**Priority**: High
**Status**: ⏸️ Not Started
**Assignee**: Claude

**User Story**:
> As a homelab sysadmin, I want to create change requests so that I can plan and track infrastructure changes.

**Acceptance Criteria**:
- [ ] Web UI form for change creation
- [ ] Required fields validated
- [ ] Change saved to database
- [ ] Success confirmation displayed
- [ ] Change viewable in change list

**BDD Scenarios**: 4 scenarios
1. Create change request with required fields (@web-ui @smoke)
2. Cannot create change without justification (@web-ui @validation)
3. Create change via CLI (@cli)
4. Create change via API (@api)

**Technical Tasks**:
- [ ] Create change creation form template
- [ ] Implement field validation
- [ ] Add CLI support for change creation
- [ ] Add API POST endpoint for changes
- [ ] Create feature file: `features/change_mgmt/create_change.feature`
- [ ] Implement step definitions
- [ ] Write BDD scenarios (4 scenarios)
- [ ] Verify all scenarios passing

**Files to Create/Modify**:
- `features/change_mgmt/create_change.feature`
- `features/steps/change_creation_steps.py`
- `tracker/html/change.item.html`
- `tracker/html/change.index.html`
- `tracker/detectors/change_validation.py`

**Dependencies**: Story 3 (Change Schema)

---

#### Story 5: View Change List
**Story Points**: 3
**Priority**: Medium
**Status**: ⏸️ Not Started
**Assignee**: Claude

**User Story**:
> As a homelab sysadmin, I want to see all change requests so that I can track planned infrastructure changes.

**Acceptance Criteria**:
- [ ] Web UI displays change list
- [ ] Changes sorted by priority and creation date
- [ ] Filter by status, priority, category
- [ ] Click change to view details

**BDD Scenarios**: 2 scenarios
1. View list of changes (@web-ui)
2. Filter changes by category (@web-ui)

**Technical Tasks**:
- [ ] Create change list template
- [ ] Implement sorting (priority, creation date)
- [ ] Add filtering UI (status, priority, category)
- [ ] Create feature file: `features/change_mgmt/view_changes.feature`
- [ ] Implement step definitions
- [ ] Write BDD scenarios (2 scenarios)
- [ ] Verify all scenarios passing

**Files to Create/Modify**:
- `features/change_mgmt/view_changes.feature`
- `features/steps/view_changes_steps.py`
- `tracker/html/change.index.html`

**Dependencies**: Story 4 (Create Change)

---

### Documentation Tasks

#### Task D1: Tutorial - Understanding ITIL Workflows
**Priority**: Medium
**Estimate**: 2 hours
**Status**: ⏸️ Not Started

**Subtasks**:
- [ ] Explain ITIL incident management basics
- [ ] Show issue lifecycle in PMS
- [ ] Provide examples of status transitions
- [ ] Include workflow diagrams
- [ ] Review and edit

**File**: `docs/tutorials/itil-workflows.md`

**Dependencies**: Story 1

---

#### Task D2: Reference - Issue Status Transitions
**Priority**: Medium
**Estimate**: 1 hour
**Status**: ⏸️ Not Started

**Subtasks**:
- [ ] Document all valid status transitions
- [ ] Create transition matrix table
- [ ] Explain transition rules
- [ ] Add troubleshooting section

**File**: `docs/reference/status-transitions.md`

**Dependencies**: Story 1

---

#### Task D3: Reference - Change Request Schema
**Priority**: Medium
**Estimate**: 1 hour
**Status**: ⏸️ Not Started

**Subtasks**:
- [ ] Document all change fields
- [ ] Explain field purposes
- [ ] Provide examples
- [ ] Include validation rules

**File**: `docs/reference/change-schema.md`

**Dependencies**: Story 3

---

#### Task D4: Update CHANGELOG for v0.3.0
**Priority**: High
**Estimate**: 30 minutes
**Status**: ⏸️ Not Started

**Subtasks**:
- [ ] Document all changes in CHANGELOG.md
- [ ] Update version links
- [ ] Review changelog format

**Dependencies**: All stories complete

---

## Progress Tracking

### Story Points Progress
```
[##############______________] 14/27 (52%)
```

### BDD Scenarios Progress
**Target**: 20+ scenarios
**Current**: 15 passing (75% of minimum target)

- [x] Issue workflow: 7 scenarios **ALL PASSING** ✅
- [x] Assign issues: 4 scenarios **ALL PASSING** ✅
- [x] Change schema: 4 scenarios **ALL PASSING** ✅
- [ ] Create change: 4 scenarios
- [ ] View changes: 2 scenarios

### Test Coverage
**Target**: >85%
**Current**: TBD

---

## Definition of Done Checklist

- [ ] All user stories completed with acceptance criteria met
- [ ] All BDD scenarios implemented and passing (13 scenarios)
- [ ] Issue workflow enforces valid transitions
- [ ] Change management schema functional
- [ ] Code passes pre-commit hooks (ruff, mypy, gitleaks)
- [ ] ITIL workflows tutorial published
- [ ] Test coverage >85% for new code
- [ ] CHANGELOG.md updated for v0.3.0
- [ ] Sprint retrospective completed
- [ ] GitHub Actions CI/CD passing

---

## Risk Register

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Workflow complexity higher than expected | High | Medium | Start with simple linear workflow, iterate |
| Database schema migration issues | Medium | Low | Test migrations separately, backup before applying |
| Roundup detector limitations | Medium | Medium | Research detector capabilities early, plan workarounds |
| Time estimation inaccurate | Low | High | Track actual vs estimated time, adjust for next sprint |

---

## Sprint Velocity

**Previous Sprint (Sprint 1)**: 19/27 story points completed (70%)
**This Sprint Target**: 27 story points
**Estimated Completion**: Based on Sprint 1 velocity, expect ~20 story points

---

## Notes

- Follow BDD-first approach: write scenarios before implementation
- Test status workflow thoroughly to prevent data inconsistencies
- Document ITIL concepts for educational value
- Keep change management simple for v0.3.0, iterate in future sprints
- Use Roundup detectors for workflow validation where possible
