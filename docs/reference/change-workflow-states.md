<!--
SPDX-FileCopyrightText: 2025 Georges Martin <jrjsmrtn@gmail.com>
SPDX-License-Identifier: MIT
-->

# Reference: Change Workflow States

**Type**: Reference documentation
**Audience**: Developers, system administrators, integrators
**Purpose**: Technical specification of all change workflow states and transitions

## Overview

The Pasture Management System implements an ITIL-inspired change workflow with eight distinct states and strictly enforced transition rules. This reference documents all states, valid transitions, required fields, and validation rules.

## State Definitions

### Planning

**Roundup ID**: `1`
**Display Name**: "Planning"
**Description**: Initial state when a change request is created

**Purpose**: Capture the initial change request with justification and basic details before formal assessment begins.

**Required Fields**:

- `title` (String, 1-255 characters)
- `description` (Text)
- `justification` (Text)
- `priority` (Link to priority: Critical=4, High=3, Medium=2, Low=1)
- `category` (Link to category: Hardware=1, Software=2, Network=3, Configuration=4, Documentation=5)
- `creator` (Link to user, auto-set on creation)
- `created` (Date, auto-set on creation)

**Optional Fields**:

- `impact` (Text)
- `risk` (Text)
- `linked_issues` (Multilink to issue)

**Valid Transitions**:

- → `Assessment` (via "Start Assessment" action)
- → `Cancelled` (via "Cancel" action)

**Validation Rules**:

- Cannot transition to Approved without passing through Assessment
- Cannot set scheduled_start/scheduled_end while in Planning

______________________________________________________________________

### Assessment

**Roundup ID**: `2`
**Display Name**: "Assessment"
**Description**: Change is being evaluated for risk, impact, and feasibility

**Purpose**: Formal assessment phase where risk and impact are evaluated before approval decision.

**Required Fields** (inherited from Planning, plus):

- `impact` (Text) - Service impact assessment
- `risk` (Text) - Risk level and mitigation plan

**Valid Transitions**:

- → `Approved` (via "Approve" action, requires impact and risk)
- → `Rejected` (via "Reject" action, requires rejection_reason)
- → `Planning` (via "Back to Planning" action)
- → `Cancelled` (via "Cancel" action)

**Validation Rules**:

- High-risk changes (risk level "High" or "Very High") require detailed mitigation plan
- Impact assessment must identify affected services and estimated downtime
- Approval requires both impact and risk fields to be non-empty

**Notes**:

- This is the decision point in the workflow
- Rejection requires documented reason
- Can return to Planning for more information

______________________________________________________________________

### Approved

**Roundup ID**: `3`
**Display Name**: "Approved"
**Description**: Change has been approved and is ready for scheduling

**Purpose**: Change has passed assessment and is authorized to proceed; awaiting schedule.

**Required Fields** (inherited from Assessment):

- All Planning and Assessment fields must be complete

**Optional Fields**:

- `approval_notes` (Text) - Approval comments
- `approver` (Link to user) - Who approved the change

**Valid Transitions**:

- → `Scheduled` (via "Schedule" action, requires scheduled_start and scheduled_end)
- → `Assessment` (via "Re-assess" action, if requirements change)
- → `Cancelled` (via "Cancel" action)

**Validation Rules**:

- Cannot transition to Scheduled without valid scheduled_start and scheduled_end times
- scheduled_end must be after scheduled_start
- Cannot skip directly to Implementing (must go through Scheduled)

______________________________________________________________________

### Rejected

**Roundup ID**: `4`
**Display Name**: "Rejected"
**Description**: Change has been rejected and will not be implemented

**Purpose**: Terminal state for changes that failed assessment or approval.

**Required Fields**:

- `rejection_reason` (Text) - Why the change was rejected

**Optional Fields**:

- `rejection_notes` (Text) - Additional details
- `rejected_by` (Link to user) - Who rejected the change
- `rejected_date` (Date) - When rejection occurred

**Valid Transitions**:

- → `Planning` (via "Reopen" action, creates new change request)

**Validation Rules**:

- Rejection requires non-empty rejection_reason
- Cannot transition to any state except Planning (reopen creates new change)

**Notes**:

- This is a terminal state (end of workflow)
- Reopening creates a new change request with lessons learned

______________________________________________________________________

### Scheduled

**Roundup ID**: `5`
**Display Name**: "Scheduled"
**Description**: Change is approved and scheduled for a specific maintenance window

**Purpose**: Change has a confirmed implementation window and is awaiting execution.

**Required Fields**:

- `scheduled_start` (Date) - When implementation will begin
- `scheduled_end` (Date) - When implementation should complete

**Optional Fields**:

- `scheduled_notes` (Text) - Scheduling details, dependencies, prerequisites

**Valid Transitions**:

- → `Implementing` (via "Start Implementation" action, sets actual_start)
- → `Approved` (via "Reschedule" action, allows changing scheduled times)
- → `Cancelled` (via "Cancel" action)

**Validation Rules**:

- scheduled_end must be after scheduled_start
- Rescheduling is allowed but history must be preserved
- Cannot start implementation before scheduled_start time (warning only)

**Notes**:

- Changes can be rescheduled multiple times before implementation
- Scheduled changes appear in maintenance calendar
- Notifications can be configured for upcoming scheduled changes

______________________________________________________________________

### Implementing

**Roundup ID**: `6`
**Display Name**: "Implementing"
**Description**: Change implementation is currently in progress

**Purpose**: Active implementation phase; actual execution is underway.

**Required Fields**:

- `actual_start` (Date) - Auto-set when transitioning to Implementing

**Optional Fields**:

- `implementation_notes` (Text) - Real-time notes during implementation
- `implementer` (Link to user) - Who is performing the change

**Valid Transitions**:

- → `Completed` (via "Mark Complete" action, sets actual_end)
- → `Cancelled` (via "Rollback" action, requires rollback_reason and rollback_notes)

**Validation Rules**:

- actual_start automatically set to current timestamp on transition
- Cannot transition back to Scheduled (must complete or rollback)
- Completion sets actual_end automatically

**Notes**:

- This is the critical execution phase
- Implementation notes should be updated in real-time
- Rollback is available if issues arise

______________________________________________________________________

### Completed

**Roundup ID**: `7`
**Display Name**: "Completed"
**Description**: Change has been successfully implemented

**Purpose**: Terminal state for successful changes; implementation complete.

**Required Fields**:

- `actual_start` (Date) - When implementation began
- `actual_end` (Date) - When implementation completed
- `implementation_outcome` (String) - "Success" or "Success with deviations"

**Optional Fields**:

- `implementation_notes` (Text) - What was actually done
- `deviation_notes` (Text) - If things didn't go as planned
- `actual_duration` (Interval) - Calculated from actual_start to actual_end

**Valid Transitions**:

- None (terminal state)

**Validation Rules**:

- actual_end must be after actual_start
- If implementation_outcome is "Success with deviations", deviation_notes should be provided
- Cannot modify status after completion (immutable record)

**Post-Completion**:

- Linked issues can be updated to reflect change completion
- Post-implementation review can be documented in notes
- Change record preserved for audit trail

**Notes**:

- This is a terminal state (end of successful workflow)
- Immutable historical record
- Used for metrics and reporting

______________________________________________________________________

### Cancelled

**Roundup ID**: `8`
**Display Name**: "Cancelled"
**Description**: Change was cancelled or rolled back

**Purpose**: Terminal state for cancelled changes or failed implementations requiring rollback.

**Required Fields** (if cancelled from Implementing):

- `rollback_reason` (Text) - Why rollback was necessary
- `rollback_notes` (Text) - What was done to rollback

**Optional Fields**:

- `cancellation_reason` (Text) - If cancelled before implementation
- `cancelled_by` (Link to user)
- `cancelled_date` (Date)

**Valid Transitions**:

- → `Planning` (via "Create New Change" action, for retry)

**Validation Rules**:

- Rollback from Implementing requires both rollback_reason and rollback_notes
- Cancellation from Planning/Assessment/Approved/Scheduled requires cancellation_reason
- Cannot un-cancel (must create new change request)

**Notes**:

- This is a terminal state
- Captures lessons learned for future attempts
- Rollback documentation critical for post-incident review

______________________________________________________________________

## State Transition Matrix

| From \\ To       | Planning | Assessment | Approved | Rejected | Scheduled | Implementing | Completed | Cancelled |
| ---------------- | -------- | ---------- | -------- | -------- | --------- | ------------ | --------- | --------- |
| **Planning**     | -        | ✅         | ❌       | ❌       | ❌        | ❌           | ❌        | ✅        |
| **Assessment**   | ✅       | -          | ✅       | ✅       | ❌        | ❌           | ❌        | ✅        |
| **Approved**     | ❌       | ✅         | -        | ❌       | ✅        | ❌           | ❌        | ✅        |
| **Rejected**     | ✅       | ❌         | ❌       | -        | ❌        | ❌           | ❌        | ❌        |
| **Scheduled**    | ❌       | ❌         | ✅       | ❌       | -         | ✅           | ❌        | ✅        |
| **Implementing** | ❌       | ❌         | ❌       | ❌       | ❌        | -            | ✅        | ✅        |
| **Completed**    | ❌       | ❌         | ❌       | ❌       | ❌        | ❌           | -         | ❌        |
| **Cancelled**    | ✅       | ❌         | ❌       | ❌       | ❌        | ❌           | ❌        | -         |

**Legend**:

- ✅ = Valid transition
- ❌ = Invalid transition
- `-` = Current state

______________________________________________________________________

## Workflow Paths

### Standard Success Path

```
Planning → Assessment → Approved → Scheduled → Implementing → Completed
```

**Description**: Normal change workflow from request to successful completion.

**Typical Duration**: 1-7 days (Planning to Approved), variable (Scheduled to Completed based on maintenance window)

______________________________________________________________________

### Assessment Rejection Path

```
Planning → Assessment → Rejected
```

**Description**: Change fails assessment and is rejected.

**Can Resume**: Yes, via "Reopen" action which creates new change request with lessons learned.

______________________________________________________________________

### Rollback Path

```
Planning → Assessment → Approved → Scheduled → Implementing → Cancelled
```

**Description**: Implementation fails and must be rolled back.

**Required Documentation**: rollback_reason, rollback_notes must document what went wrong and how rollback was performed.

______________________________________________________________________

### Cancellation Paths

```
Planning → Cancelled
Assessment → Cancelled
Approved → Cancelled
Scheduled → Cancelled
```

**Description**: Change cancelled before implementation begins.

**Required Documentation**: cancellation_reason should explain why change is no longer needed.

______________________________________________________________________

### Re-assessment Path

```
Planning → Assessment → Approved → Assessment → Approved → Scheduled
```

**Description**: Approved change requires re-assessment due to changed requirements.

**Use Case**: Requirements change, new risks identified, scope expansion needed.

______________________________________________________________________

### Rescheduling Path

```
... → Scheduled → Approved → Scheduled → Implementing
```

**Description**: Scheduled change needs different maintenance window.

**Use Case**: Conflict with other changes, prerequisite not met, resource unavailable.

______________________________________________________________________

## Field Requirements by State

| Field                  | Planning | Assessment | Approved | Rejected | Scheduled | Implementing | Completed | Cancelled |
| ---------------------- | -------- | ---------- | -------- | -------- | --------- | ------------ | --------- | --------- |
| title                  | ✅       | ✅         | ✅       | ✅       | ✅        | ✅           | ✅        | ✅        |
| description            | ✅       | ✅         | ✅       | ✅       | ✅        | ✅           | ✅        | ✅        |
| justification          | ✅       | ✅         | ✅       | ✅       | ✅        | ✅           | ✅        | ✅        |
| priority               | ✅       | ✅         | ✅       | ✅       | ✅        | ✅           | ✅        | ✅        |
| category               | ✅       | ✅         | ✅       | ✅       | ✅        | ✅           | ✅        | ✅        |
| impact                 | 📝       | ✅         | ✅       | ✅       | ✅        | ✅           | ✅        | ✅        |
| risk                   | 📝       | ✅         | ✅       | ✅       | ✅        | ✅           | ✅        | ✅        |
| rejection_reason       | -        | -          | -        | ✅       | -         | -            | -         | 📝        |
| scheduled_start        | -        | -          | -        | -        | ✅        | ✅           | ✅        | 📝        |
| scheduled_end          | -        | -          | -        | -        | ✅        | ✅           | ✅        | 📝        |
| actual_start           | -        | -          | -        | -        | -         | ✅           | ✅        | 📝        |
| actual_end             | -        | -          | -        | -        | -         | -            | ✅        | 📝        |
| implementation_notes   | -        | -          | -        | -        | -         | 📝           | 📝        | 📝        |
| implementation_outcome | -        | -          | -        | -        | -         | -            | ✅        | -         |
| rollback_reason        | -        | -          | -        | -        | -         | -            | -         | 📝        |
| rollback_notes         | -        | -          | -        | -        | -         | -            | -         | 📝        |

**Legend**:

- ✅ = Required field
- 📝 = Optional but recommended
- `-` = Not applicable

______________________________________________________________________

## API State Transitions

### Transition Endpoints

All state transitions are performed via PATCH requests to `/api/change/{id}` with JSON payload.

#### Start Assessment

```http
PATCH /api/change/1
Content-Type: application/json

{
  "status": "2"
}
```

**Validation**: Must be in Planning state.

______________________________________________________________________

#### Approve Change

```http
PATCH /api/change/1
Content-Type: application/json

{
  "status": "3",
  "approval_notes": "Risk assessment complete, approved for scheduled maintenance"
}
```

**Validation**:

- Must be in Assessment state
- Requires non-empty `impact` field
- Requires non-empty `risk` field

______________________________________________________________________

#### Reject Change

```http
PATCH /api/change/1
Content-Type: application/json

{
  "status": "4",
  "rejection_reason": "Conflicts with security policy, insufficient testing"
}
```

**Validation**: Must be in Assessment state, requires `rejection_reason`.

______________________________________________________________________

#### Schedule Change

```http
PATCH /api/change/1
Content-Type: application/json

{
  "status": "5",
  "scheduled_start": "2025-12-01T02:00:00Z",
  "scheduled_end": "2025-12-01T04:00:00Z"
}
```

**Validation**:

- Must be in Approved state
- `scheduled_end` must be after `scheduled_start`

______________________________________________________________________

#### Start Implementation

```http
PATCH /api/change/1
Content-Type: application/json

{
  "status": "6"
}
```

**Validation**: Must be in Scheduled state. `actual_start` auto-set to current timestamp.

______________________________________________________________________

#### Complete Change

```http
PATCH /api/change/1
Content-Type: application/json

{
  "status": "7",
  "implementation_outcome": "success",
  "implementation_notes": "Database upgraded successfully, all tests passed"
}
```

**Validation**: Must be in Implementing state. `actual_end` auto-set to current timestamp.

______________________________________________________________________

#### Rollback Change

```http
PATCH /api/change/1
Content-Type: application/json

{
  "status": "8",
  "rollback_reason": "Migration failed validation tests",
  "rollback_notes": "Restored from backup, verified all services operational"
}
```

**Validation**:

- Must be in Implementing state
- Requires both `rollback_reason` and `rollback_notes`

______________________________________________________________________

#### Cancel Change

```http
PATCH /api/change/1
Content-Type: application/json

{
  "status": "8",
  "cancellation_reason": "Change no longer required due to alternative solution"
}
```

**Validation**: Can be done from Planning, Assessment, Approved, or Scheduled states. Requires `cancellation_reason`.

______________________________________________________________________

## CLI State Transitions

### Basic Syntax

```bash
roundup-admin -i tracker set change{id} status={status_id} [additional_fields]
```

### Examples

**Start Assessment**:

```bash
roundup-admin -i tracker set change1 status=2
```

**Approve**:

```bash
roundup-admin -i tracker set change1 status=3 \
  approval_notes="Risk assessment complete, approved"
```

**Reject**:

```bash
roundup-admin -i tracker set change1 status=4 \
  rejection_reason="Insufficient testing, conflicts with policy"
```

**Schedule**:

```bash
roundup-admin -i tracker set change1 status=5 \
  scheduled_start="2025-12-01.02:00:00" \
  scheduled_end="2025-12-01.04:00:00"
```

**Start Implementation**:

```bash
roundup-admin -i tracker set change1 status=6
```

**Complete**:

```bash
roundup-admin -i tracker set change1 status=7 \
  implementation_outcome="success" \
  implementation_notes="Upgrade successful, all tests passed"
```

**Rollback**:

```bash
roundup-admin -i tracker set change1 status=8 \
  rollback_reason="Migration failed validation" \
  rollback_notes="Restored from backup, services verified"
```

______________________________________________________________________

## Validation Rules

### State Transition Validation

Implemented in Roundup detector: `customizations/detectors/change_workflow.py`

**Rules**:

1. Invalid transitions return HTTP 400 with error message
1. Missing required fields block state transition
1. State history is preserved in audit trail
1. Timestamps are automatically managed for critical events

### Field Validation

**Title**:

- Required: Yes
- Type: String
- Length: 1-255 characters
- Cannot be empty or whitespace-only

**Description**:

- Required: Yes
- Type: Text
- Length: Unlimited
- Should be detailed implementation plan

**Priority**:

- Required: Yes
- Type: Link
- Valid values: 1 (Low), 2 (Medium), 3 (High), 4 (Critical)

**Category**:

- Required: Yes
- Type: Link
- Valid values: 1 (Hardware), 2 (Software), 3 (Network), 4 (Configuration), 5 (Documentation)

**Scheduled Times**:

- Format: "YYYY-MM-DD.HH:MM:SS" (Roundup format)
- Validation: end > start
- Timezone: UTC

**Actual Times**:

- Auto-set on state transitions
- Cannot be manually modified
- Preserved for audit trail

______________________________________________________________________

## State History

Every state transition is recorded in the change history with:

- Previous state
- New state
- User who made the transition
- Timestamp
- Any notes or comments

**Query State History** (CLI):

```bash
roundup-admin -i tracker history change1
```

**Response Example**:

```
1: 2025-11-16.14:00:00 by admin: created
2: 2025-11-16.14:15:00 by admin: status -> Planning (1)
3: 2025-11-16.14:30:00 by admin: status -> Assessment (2)
4: 2025-11-16.15:00:00 by admin: status -> Approved (3), approval_notes="Risk assessment complete"
5: 2025-11-16.15:30:00 by admin: status -> Scheduled (5), scheduled_start="2025-12-01.02:00:00"
```

______________________________________________________________________

## Common Patterns

### Emergency Change (Fast-Track)

For critical security patches or urgent fixes:

```
Planning → Assessment (rapid) → Approved → Implementing → Completed
         (minutes)             (minutes)  (immediate)
```

**Notes**:

- Skip Scheduled state if implementation must be immediate
- Document emergency justification
- Post-implementation review recommended

### Standard Maintenance

For planned maintenance windows:

```
Planning → Assessment → Approved → Scheduled → Implementing → Completed
(1-2 days) (1-2 days)  (days)    (hours-days) (scheduled)
```

### Iterative Refinement

For complex changes requiring multiple assessment cycles:

```
Planning → Assessment → Planning → Assessment → Approved → ...
           (feedback)   (revision)  (approval)
```

______________________________________________________________________

## Error Codes

**E001**: Invalid state transition
**E002**: Missing required field for state
**E003**: Invalid scheduled times (end before start)
**E004**: Cannot modify completed or cancelled change
**E005**: Approval without risk/impact assessment
**E006**: Rollback without reason/notes

______________________________________________________________________

## Related Documentation

- **Tutorial**: Managing Changes in Your Homelab - Hands-on workflow walkthrough
- **How-to**: Submitting a Change Request - Creating changes
- **How-to**: Assessing Change Risk - Risk evaluation process
- **Explanation**: ITIL Change Management Principles - Methodology background

______________________________________________________________________

## Schema Definition

See `customizations/schema/change.py` for complete field definitions and validation rules.

**Key Classes**:

- `Change` - Main change class
- `ChangeStatus` - Status enumeration
- `ChangeCategory` - Category enumeration
- `ChangePriority` - Priority enumeration

______________________________________________________________________

**Last Updated**: 2025-11-16
**Version**: 0.4.0
**Status**: Draft (pending implementation)
