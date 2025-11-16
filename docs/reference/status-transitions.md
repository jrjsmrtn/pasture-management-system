<!--
SPDX-FileCopyrightText: 2025 Georges Martin <jrjsmrtn@gmail.com>
SPDX-License-Identifier: MIT
-->

# Issue Status Transitions Reference

This document provides the complete technical reference for issue status transitions in the Pasture Management System (PMS).

## Status Values

### Issue Statuses

| ID  | Name        | Order | Description                                      |
| --- | ----------- | ----- | ------------------------------------------------ |
| 1   | new         | 1     | Issue has been created but not yet started       |
| 2   | in-progress | 2     | Issue is actively being worked on                |
| 3   | resolved    | 3     | Fix has been implemented and awaits verification |
| 4   | closed      | 4     | Issue has been verified and is complete          |

### Database Schema

```python
# From tracker/schema.py
stat = Class(db, "status",
    name=String(),
    order=Number())
stat.setkey("name")

# From tracker/initial_data.py
db.status.create(name="new", order=1)
db.status.create(name="in-progress", order=2)
db.status.create(name="resolved", order=3)
db.status.create(name="closed", order=4)
```

## Transition Matrix

### Valid Transitions

| From Status | To Status   | Allowed | Typical Use Case                        |
| ----------- | ----------- | ------- | --------------------------------------- |
| new         | in-progress | ✅ Yes  | Begin working on the issue              |
| new         | resolved    | ❌ No   | Cannot skip investigation phase         |
| new         | closed      | ❌ No   | Cannot close without fixing             |
| in-progress | new         | ❌ No   | Cannot revert to new                    |
| in-progress | resolved    | ✅ Yes  | Fix implemented, ready for verification |
| in-progress | closed      | ❌ No   | Must verify fix first                   |
| resolved    | new         | ❌ No   | Cannot revert to new                    |
| resolved    | in-progress | ✅ Yes  | Fix didn't work, need to rework         |
| resolved    | closed      | ✅ Yes  | Fix verified, issue complete            |
| closed      | new         | ❌ No   | Cannot reopen as new                    |
| closed      | in-progress | ❌ No   | Cannot reopen directly                  |
| closed      | resolved    | ❌ No   | Cannot unresolve                        |

### Transition Rules Summary

**Allowed transitions**:

- `new` → `in-progress`
- `in-progress` → `resolved`
- `resolved` → `closed`
- `resolved` → `in-progress` (rework only)

**Blocked transitions**: All others

## Implementation Details

### Validation Detector

Status transitions are enforced by the `status_workflow.py` detector:

**Location**: `tracker/detectors/status_workflow.py`

**Key Function**:

```python
def check_status_transition(db, cl, nodeid, newvalues):
    """Validate status transitions follow ITIL workflow rules."""

    # Get current and new status
    current_status_id = cl.get(nodeid, 'status')
    new_status_id = newvalues.get('status')

    # If status unchanged, allow
    if current_status_id == new_status_id:
        return

    # Define valid transitions
    VALID_TRANSITIONS = {
        '1': ['2'],        # new -> in-progress
        '2': ['3'],        # in-progress -> resolved
        '3': ['2', '4'],   # resolved -> in-progress OR closed
        '4': []            # closed (terminal state)
    }

    # Validate transition
    allowed = VALID_TRANSITIONS.get(current_status_id, [])
    if new_status_id not in allowed:
        raise ValueError(f"Invalid status transition")
```

**Registration**:

```python
def init(db):
    db.issue.audit('set', check_status_transition, priority=100)
```

### Error Messages

When an invalid transition is attempted:

**Web UI**:

```
Invalid status transition from 'new' to 'closed'.
Valid transitions from 'new': in-progress
```

**CLI**:

```bash
$ roundup-admin -i tracker set issue1 status=4
Error: Invalid status transition from status '1' (new) to '4' (closed)
Valid transitions: 2 (in-progress)
```

**API**:

```json
{
  "error": {
    "status": 400,
    "msg": "Invalid status transition from 'new' to 'closed'"
  }
}
```

## Status History Tracking

### Automatic Tracking

Every status change is automatically recorded in the issue's journal:

**Journal Entry Format**:

```
<date> <time> <username> set status: <old_status> -> <new_status>
```

**Example**:

```
2025-11-16 10:30:00 admin set status: new -> in-progress
2025-11-16 11:45:00 admin set status: in-progress -> resolved
2025-11-16 14:20:00 admin set status: resolved -> closed
```

### Viewing History

**Web UI**: Issue details page → "History" section

**CLI**:

```bash
roundup-admin -i tracker history issue1
```

**API**:

```bash
curl http://localhost:8080/pms/api/issues/1/history \
  -u admin:admin
```

## Transition Triggers

### Web UI Buttons

The Web UI displays context-sensitive buttons based on current status:

| Current Status | Available Buttons                                    |
| -------------- | ---------------------------------------------------- |
| new            | "Start Work" (→ in-progress)                         |
| in-progress    | "Mark Resolved" (→ resolved)                         |
| resolved       | "Close Issue" (→ closed)<br>"Reopen" (→ in-progress) |
| closed         | (no transitions available)                           |

**Template**: `tracker/html/issue.item.html`

**Button Logic**:

```html
<tal:block tal:condition="python:issue.status.id == '1'">
  <!-- Show "Start Work" button -->
  <input type="submit" name="status" value="2"
         title="Start Work">
</tal:block>

<tal:block tal:condition="python:issue.status.id == '2'">
  <!-- Show "Mark Resolved" button -->
  <input type="submit" name="status" value="3"
         title="Mark Resolved">
</tal:block>
```

### CLI Transitions

Using `roundup-admin`:

```bash
# Transition new → in-progress
roundup-admin -i tracker set issue1 status=2

# Transition in-progress → resolved
roundup-admin -i tracker set issue1 status=3

# Transition resolved → closed
roundup-admin -i tracker set issue1 status=4

# Transition resolved → in-progress (rework)
roundup-admin -i tracker set issue3 status=2
```

### API Transitions

Using REST API with PATCH:

```bash
# Transition new → in-progress
curl -X PATCH http://localhost:8080/pms/api/issues/1 \
  -H "Content-Type: application/json" \
  -H "X-Requested-With: XMLHttpRequest" \
  -u admin:admin \
  -d '{"status": "2"}'

# Transition in-progress → resolved
curl -X PATCH http://localhost:8080/pms/api/issues/1 \
  -H "Content-Type: application/json" \
  -H "X-Requested-With: XMLHttpRequest" \
  -u admin:admin \
  -d '{"status": "3"}'
```

**Response (Success)**:

```json
{
  "data": {
    "id": "1",
    "type": "issue",
    "attributes": {
      "status": "3"
    }
  }
}
```

**Response (Validation Error)**:

```json
{
  "error": {
    "status": 400,
    "msg": "Invalid status transition from 'new' to 'closed'"
  }
}
```

## Workflow Customization

### Adding New Statuses

To add custom statuses:

1. **Update initial_data.py**:

```python
db.status.create(name="on-hold", order=5)
```

2. **Update transition rules** in `tracker/detectors/status_workflow.py`:

```python
VALID_TRANSITIONS = {
    '1': ['2'],           # new -> in-progress
    '2': ['3', '5'],      # in-progress -> resolved OR on-hold
    '3': ['2', '4'],      # resolved -> in-progress OR closed
    '4': [],              # closed (terminal)
    '5': ['2'],           # on-hold -> in-progress
}
```

3. **Reinitialize database**:

```bash
rm -rf tracker/db
roundup-admin -i tracker initialise
```

### Modifying Transition Rules

To allow new transitions:

1. Edit `tracker/detectors/status_workflow.py`
1. Update `VALID_TRANSITIONS` dictionary
1. Restart tracker
1. Update documentation

**Example**: Allow direct new → resolved:

```python
VALID_TRANSITIONS = {
    '1': ['2', '3'],  # Allow new -> resolved
    # ...
}
```

## Troubleshooting

### Issue Stuck in Wrong Status

**Problem**: Issue accidentally set to wrong status

**Solution**: Use CLI to force correct status (if transition is valid):

```bash
roundup-admin -i tracker set issue1 status=2
```

**If transition blocked**: Work backwards through valid transitions:

```bash
# If resolved but should be in-progress:
# (resolved → in-progress is valid)
roundup-admin -i tracker set issue1 status=2
```

### Cannot Transition to Desired Status

**Problem**: Web UI button missing or CLI/API returns error

**Diagnosis**: Check current status and transition matrix above

**Solution**: Follow valid transition path:

```bash
# To go from new to closed:
# Must go: new → in-progress → resolved → closed
roundup-admin -i tracker set issue1 status=2  # Step 1
roundup-admin -i tracker set issue1 status=3  # Step 2
roundup-admin -i tracker set issue1 status=4  # Step 3
```

### Validation Detector Not Working

**Problem**: Invalid transitions allowed

**Diagnosis**: Check detector is registered:

```bash
roundup-admin -i tracker list detectors
```

**Solution**: Ensure `status_workflow.py` is in `tracker/detectors/` and registered in `__init__.py`

### History Not Recording

**Problem**: Status changes not appearing in history

**Diagnosis**: Journal disabled or permissions issue

**Solution**: Check journal configuration in `tracker/schema.py`:

```python
issue = IssueClass(db, "issue",
    # ... fields ...
    status=Link("status"))  # Journal enabled by default
```

## Performance Considerations

### Query Optimization

When filtering by status:

```bash
# Efficient: Use status ID
roundup-admin -i tracker filter issue status=2

# Less efficient: Use status name (requires join)
roundup-admin -i tracker filter issue status.name=in-progress
```

### Index Recommendations

For large deployments (1000+ issues):

```sql
CREATE INDEX idx_issue_status ON _issue(status);
CREATE INDEX idx_issue_status_priority ON _issue(status, priority);
```

## Related Documentation

- [Tutorial: Understanding ITIL Workflows](../tutorials/understanding-itil-workflows.md) - Learn workflow concepts
- [How-to: Change Issue Status](../howto/change-issue-status.md) - Step-by-step guides
- [Architecture Decision Record: ITIL Workflows](../adr/0004-itil-workflows.md) - Design rationale

## Changelog

| Version | Date       | Changes                                |
| ------- | ---------- | -------------------------------------- |
| 0.3.0   | 2025-11-16 | Initial implementation with 4 statuses |

______________________________________________________________________

**Maintained by**: Pasture Management System project
**Last updated**: 2025-11-16
**Applies to**: PMS v0.3.0+
