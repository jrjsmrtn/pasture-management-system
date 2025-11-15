<!--
SPDX-FileCopyrightText: 2025 Georges Martin <jrjsmrtn@gmail.com>
SPDX-License-Identifier: MIT
-->

# Change Request Schema Reference

This document provides the complete technical reference for change requests in the Pasture Management System (PMS).

## Overview

Change requests are used to plan and track infrastructure changes in a controlled, systematic way following ITIL Change Management principles. Unlike issues (which are reactive responses to problems), changes are proactive modifications to your homelab infrastructure.

## Class Definition

### Change Class

**Base Class**: `IssueClass`
**Location**: `tracker/schema.py`

```python
change = IssueClass(db, "change",
    description=String(),           # Detailed description
    justification=String(),         # Business justification
    impact=String(),                # Impact assessment
    risk=String(),                  # Risk assessment
    assignedto=Link("user"),        # Change owner
    priority=Link("changepriority"), # Change priority
    category=Link("changecategory"), # Change category
    status=Link("changestatus"),    # Workflow status
    related_issues=Multilink("issue")) # Related issues
```

### Inherited Fields

From `IssueClass`:

| Field | Type | Description |
|-------|------|-------------|
| title | String | Short summary of the change |
| messages | Multilink("msg") | Discussion and updates |
| files | Multilink("file") | Attachments (diagrams, configs, etc.) |
| nosy | Multilink("user") | Users to notify about updates |
| superseder | Multilink("change") | Related parent changes |

From `Class` (automatic):

| Field | Type | Description |
|-------|------|-------------|
| creation | Date | When change was created |
| activity | Date | Last modification timestamp |
| creator | Link("user") | User who created the change |
| actor | Link("user") | User who last modified the change |

## Field Specifications

### Required Fields

| Field | Type | Required | Validation |
|-------|------|----------|------------|
| title | String | ✅ Yes | Non-empty, max 255 chars |
| justification | String | ✅ Yes | Non-empty |
| priority | Link | ✅ Yes | Must be valid changepriority ID |
| category | Link | ✅ Yes | Must be valid changecategory ID |

### Optional Fields

| Field | Type | Required | Default | Validation |
|-------|------|----------|---------|------------|
| description | String | ❌ No | Empty | Max 64KB |
| impact | String | ❌ No | Empty | Max 16KB |
| risk | String | ❌ No | Empty | Max 16KB |
| assignedto | Link("user") | ❌ No | None | Must be valid user ID |
| status | Link("changestatus") | ❌ No | 1 (Planning) | Must be valid status ID |
| related_issues | Multilink("issue") | ❌ No | [] | Must be valid issue IDs |

## Change Priorities

### Priority Values

| ID | Name | Order | Use When |
|----|------|-------|----------|
| 1 | Low | 1 | Cosmetic improvements, non-critical enhancements |
| 2 | Medium | 2 | Planned upgrades, performance improvements |
| 3 | High | 3 | Security patches, important feature additions |
| 4 | Critical | 4 | Emergency fixes, critical security updates |

### Schema Definition

```python
changepriority = Class(db, "changepriority",
    name=String(),
    order=Number())
changepriority.setkey("name")

# Initial data
db.changepriority.create(name="Low", order=1)
db.changepriority.create(name="Medium", order=2)
db.changepriority.create(name="High", order=3)
db.changepriority.create(name="Critical", order=4)
```

### Priority Selection Guide

**Critical** - Immediate action required:
- Zero-day security vulnerability
- Complete service outage imminent
- Data loss prevention

**High** - Plan within days:
- Known security vulnerability
- Performance degradation
- Major feature addition

**Medium** - Plan within weeks:
- Routine upgrades
- Minor improvements
- Proactive maintenance

**Low** - Plan when convenient:
- Cosmetic changes
- Documentation updates
- Nice-to-have features

## Change Categories

### Category Values

| ID | Name | Order | Description |
|----|------|-------|-------------|
| 1 | Software | 1 | Application upgrades, package installations |
| 2 | Hardware | 2 | Physical equipment changes |
| 3 | Configuration | 3 | Settings, parameters, tunables |
| 4 | Network | 4 | Network topology, firewall rules, routing |

### Schema Definition

```python
changecategory = Class(db, "changecategory",
    name=String(),
    order=Number())
changecategory.setkey("name")

# Initial data
db.changecategory.create(name="Software", order=1)
db.changecategory.create(name="Hardware", order=2)
db.changecategory.create(name="Configuration", order=3)
db.changecategory.create(name="Network", order=4)
```

### Category Examples

**Software**:
- Upgrade PostgreSQL 15 → 16
- Install monitoring agent
- Patch container base images

**Hardware**:
- Add RAM to server
- Replace failed disk
- Install new network switch

**Configuration**:
- Adjust backup schedule
- Tune database parameters
- Modify systemd service settings

**Network**:
- Update firewall rules
- Configure VLANs
- Change DNS settings

## Change Statuses

### Status Values

| ID | Name | Order | Description |
|----|------|-------|-------------|
| 1 | Planning | 1 | Change is being designed and scoped |
| 2 | Approved | 2 | Change has been reviewed and approved |
| 3 | Implementing | 3 | Change is actively being deployed |
| 4 | Completed | 4 | Change successfully deployed |
| 5 | Cancelled | 5 | Change cancelled before implementation |

### Schema Definition

```python
changestatus = Class(db, "changestatus",
    name=String(),
    order=Number())
changestatus.setkey("name")

# Initial data
db.changestatus.create(name="Planning", order=1)
db.changestatus.create(name="Approved", order=2)
db.changestatus.create(name="Implementing", order=3)
db.changestatus.create(name="Completed", order=4)
db.changestatus.create(name="Cancelled", order=5)
```

### Status Workflow

```
Planning → Approved → Implementing → Completed
   ↓
Cancelled
```

**Note**: Status transition validation for changes will be implemented in future sprints. Currently, all transitions are allowed.

## Field Descriptions

### title

**Type**: String
**Max Length**: 255 characters
**Required**: Yes

Short, descriptive summary of the change.

**Good Examples**:
- "Upgrade PostgreSQL from 15.3 to 16.1"
- "Add 16GB RAM to database server"
- "Configure automated backup rotation"

**Bad Examples**:
- "Change" (too vague)
- "Update software packages and configurations across all servers in the homelab environment" (too long)

### description

**Type**: String (Text)
**Max Length**: 64KB
**Required**: No

Detailed explanation of what will change and how.

**Should Include**:
- Current state
- Desired state
- Steps to implement
- Rollback procedure

**Example**:
```
Current: PostgreSQL 15.3 running on db-server
Target: PostgreSQL 16.1

Steps:
1. Backup current database
2. Install PostgreSQL 16 packages
3. Run pg_upgrade
4. Update systemd service
5. Verify replication

Rollback:
- Restore from backup if upgrade fails
- Keep PostgreSQL 15 available for 24h
```

### justification

**Type**: String (Text)
**Max Length**: 16KB
**Required**: Yes

Business or technical reason for the change.

**Should Answer**: "Why is this change necessary?"

**Examples**:
- "PostgreSQL 16 provides 30% better query performance for our monitoring queries"
- "Current SSL certificate expires in 14 days"
- "Adding RAM will eliminate OOM errors during backup operations"

### impact

**Type**: String (Text)
**Max Length**: 16KB
**Required**: No

Assessment of how the change affects services and users.

**Should Include**:
- Affected services
- Downtime required
- User impact
- Dependencies

**Example**:
```
Services Affected:
- Main database (downtime: ~30 minutes)
- Web application (read-only mode during upgrade)

User Impact:
- Users cannot create new records during upgrade window
- Historical data remains accessible

Dependencies:
- Requires coordinating with backup schedule
- Must complete before monthly reports run
```

### risk

**Type**: String (Text)
**Max Length**: 16KB
**Required**: No

Potential risks and mitigation strategies.

**Should Include**:
- What could go wrong
- Likelihood (Low/Medium/High)
- Impact if it occurs
- Mitigation plan

**Example**:
```
Risk 1: Data corruption during migration
- Likelihood: Low
- Impact: High
- Mitigation: Full backup before starting, test migration on copy first

Risk 2: Extended downtime if rollback needed
- Likelihood: Medium
- Impact: Medium
- Mitigation: Schedule during maintenance window, have rollback steps ready

Risk 3: Application compatibility issues
- Likelihood: Low
- Impact: Medium
- Mitigation: Test application against PostgreSQL 16 in dev environment first
```

### assignedto

**Type**: Link("user")
**Required**: No
**Default**: None

User responsible for implementing the change.

**Usage**:
```bash
# Assign to user ID 1 (admin)
roundup-admin -i tracker set change1 assignedto=1
```

### related_issues

**Type**: Multilink("issue")
**Required**: No
**Default**: Empty list

Issues that this change addresses or relates to.

**Usage**:
```bash
# Link change to issues 1 and 3
roundup-admin -i tracker set change1 related_issues=1,3
```

**Use Cases**:
- Change fixes a recurring issue
- Change implements feature requested in issue
- Change prevents issues from occurring

## Creating Changes

### Web UI

1. Navigate to http://localhost:8080/pms
2. Click "Changes" → "Create New Change"
3. Fill required fields:
   - Title
   - Justification
   - Priority
   - Category
4. Optionally fill:
   - Description
   - Impact
   - Risk
   - Assigned to
5. Click "Submit"

### CLI

```bash
roundup-admin -i tracker create change \
  title="Upgrade database to PostgreSQL 16" \
  justification="Performance improvements and security patches" \
  description="Detailed implementation plan..." \
  priority=2 \
  category=1 \
  status=1
```

### API

```bash
curl -X POST http://localhost:8080/pms/api/changes \
  -H "Content-Type: application/json" \
  -H "X-Requested-With: XMLHttpRequest" \
  -H "Origin: http://localhost:8080" \
  -H "Referer: http://localhost:8080/pms/" \
  -u admin:admin \
  -d '{
    "title": "Upgrade database to PostgreSQL 16",
    "justification": "Performance improvements and security patches",
    "description": "Detailed implementation plan...",
    "priority": "2",
    "category": "1"
  }'
```

## Querying Changes

### List All Changes

```bash
roundup-admin -i tracker list change
```

### Filter by Priority

```bash
# High priority changes only
roundup-admin -i tracker filter change priority=3
```

### Filter by Category

```bash
# Software changes only
roundup-admin -i tracker filter change category=1
```

### Filter by Status

```bash
# Changes in planning status
roundup-admin -i tracker filter change status=1
```

### Combine Filters

```bash
# High priority software changes
roundup-admin -i tracker filter change priority=3 category=1
```

## Validation Rules

### Field Validation

Implemented in `tracker/html/change.item.html`:

**Title**:
- Cannot be empty
- Automatically trimmed of whitespace

**Justification**:
- Cannot be empty (HTML5 `required` attribute)

**Priority**:
- Must select from dropdown (HTML5 `required` attribute)
- Must be valid changepriority ID

**Category**:
- Must select from dropdown (HTML5 `required` attribute)
- Must be valid changecategory ID

### Future Enhancements

Planned for future sprints:

- **Status Transition Validation**: Enforce workflow rules like issues
- **Approval Process**: Require approval before implementation
- **Change Windows**: Restrict implementation to maintenance windows
- **Impact Assessment**: Automated scoring based on affected services
- **Risk Matrix**: Combined priority + risk scoring

## Database Schema

### Tables Created

```sql
-- Change priorities
CREATE TABLE _changepriority (
  _id INTEGER PRIMARY KEY,
  _name TEXT UNIQUE NOT NULL,
  _order INTEGER NOT NULL,
  _creation TIMESTAMP,
  _activity TIMESTAMP,
  _creator INTEGER,
  _actor INTEGER
);

-- Change categories
CREATE TABLE _changecategory (
  _id INTEGER PRIMARY KEY,
  _name TEXT UNIQUE NOT NULL,
  _order INTEGER NOT NULL,
  _creation TIMESTAMP,
  _activity TIMESTAMP,
  _creator INTEGER,
  _actor INTEGER
);

-- Change statuses
CREATE TABLE _changestatus (
  _id INTEGER PRIMARY KEY,
  _name TEXT UNIQUE NOT NULL,
  _order INTEGER NOT NULL,
  _creation TIMESTAMP,
  _activity TIMESTAMP,
  _creator INTEGER,
  _actor INTEGER
);

-- Changes
CREATE TABLE _change (
  _id INTEGER PRIMARY KEY,
  _title TEXT NOT NULL,
  _description TEXT,
  _justification TEXT NOT NULL,
  _impact TEXT,
  _risk TEXT,
  _assignedto INTEGER REFERENCES _user(_id),
  _priority INTEGER REFERENCES _changepriority(_id) NOT NULL,
  _category INTEGER REFERENCES _changecategory(_id) NOT NULL,
  _status INTEGER REFERENCES _changestatus(_id),
  _creation TIMESTAMP,
  _activity TIMESTAMP,
  _creator INTEGER REFERENCES _user(_id),
  _actor INTEGER REFERENCES _user(_id)
);

-- Change-Issue relationships
CREATE TABLE _change_related_issues (
  _change_id INTEGER REFERENCES _change(_id),
  _issue_id INTEGER REFERENCES _issue(_id),
  PRIMARY KEY (_change_id, _issue_id)
);
```

## Security Permissions

From `tracker/schema.py`:

**Regular Users** can:
- View all changes (`View` permission)
- Create changes (`Create` permission)
- Edit changes they created (`Edit` permission)

**Anonymous Users** can:
- View changes (read-only)
- Cannot create or edit

**Administrators** can:
- Full access to all operations

## Examples

### Example 1: Security Patch

```bash
roundup-admin -i tracker create change \
  title="Apply OpenSSL security patch" \
  justification="CVE-2025-XXXX vulnerability affects web server" \
  description="Update OpenSSL 3.0.12 to 3.0.13 on all web servers" \
  impact="No downtime required - rolling restart of services" \
  risk="Low risk - patch tested in staging environment" \
  priority=3 \
  category=1
```

### Example 2: Hardware Upgrade

```bash
roundup-admin -i tracker create change \
  title="Add 32GB RAM to compute node 3" \
  justification="Current RAM insufficient for VM workloads - causing swapping" \
  description="Purchase and install 2x 16GB DDR4 ECC modules" \
  impact="Compute node 3 offline ~30 minutes. VMs migrated to other nodes." \
  risk="Medium - verify RAM compatibility before purchase" \
  priority=2 \
  category=2 \
  assignedto=1
```

### Example 3: Network Reconfiguration

```bash
roundup-admin -i tracker create change \
  title="Implement VLAN segregation for IoT devices" \
  justification="Security best practice - isolate IoT from main network" \
  description="Create VLAN 20, configure switch ports, update firewall rules" \
  impact="Brief network interruption while switch reloads. IoT devices reconnect." \
  risk="Medium - incorrect VLAN config could block IoT access" \
  priority=2 \
  category=4 \
  status=1
```

## Related Documentation

- [Tutorial: Understanding ITIL Workflows](../tutorials/understanding-itil-workflows.md)
- [How-to: Create a Change Request](../howto/create-change-request.md)
- [Reference: Issue Status Transitions](status-transitions.md)

## Changelog

| Version | Date | Changes |
|---------|------|---------|
| 0.3.0 | 2025-11-16 | Initial implementation |

---

**Maintained by**: Pasture Management System project
**Last updated**: 2025-11-16
**Applies to**: PMS v0.3.0+
