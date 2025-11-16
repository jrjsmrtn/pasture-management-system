<!--
SPDX-FileCopyrightText: 2025 Georges Martin <jrjsmrtn@gmail.com>
SPDX-License-Identifier: MIT
-->

# How-to: Submit a Change Request

**Goal**: Quickly create a well-documented change request using your preferred interface (Web UI, CLI, or API).

**Time**: 5-10 minutes

## Overview

A change request captures what you want to change and why it's necessary. Good change requests include:

- **Clear title** - What are you changing?
- **Detailed description** - How will you do it?
- **Solid justification** - Why is this change needed?
- **Appropriate priority** - How urgent is it?
- **Correct category** - What type of change is this?

## Method 1: Web UI (Recommended for Beginners)

### Steps

1. **Navigate to Changes**

   - Click "Changes" in the main navigation menu
   - Or visit: `http://localhost:8080/pms/change?@template=index`

1. **Click "Create New Change"**

1. **Fill in Required Fields**:

   | Field         | What to Enter                                         | Example                                                                              |
   | ------------- | ----------------------------------------------------- | ------------------------------------------------------------------------------------ |
   | Title         | Brief, descriptive name                               | "Upgrade PostgreSQL to v16"                                                          |
   | Description   | Detailed plan of what you'll do                       | "Backup database, stop services, run pg_upgrade, verify migration, restart services" |
   | Justification | Why this change is necessary                          | "Security patches needed, performance improvements, EOL approaching for v14"         |
   | Priority      | Critical/High/Medium/Low                              | High                                                                                 |
   | Category      | Hardware/Software/Network/Configuration/Documentation | Software                                                                             |
   | Status        | Leave as "Planning"                                   | Planning                                                                             |

1. **Optional but Recommended**:

   - **Related Issues**: Link to any issues this change addresses
   - **Impact**: Describe potential service impact
   - **Risk**: Note any risks and mitigation plans

1. **Click "Submit"**

### Result

You'll see your new change with a change ID (e.g., "change1"). The status will be "Planning".

## Method 2: CLI (Recommended for Automation)

### Basic Syntax

```bash
roundup-admin -i tracker create change \
  title="<title>" \
  description="<description>" \
  justification="<justification>" \
  priority=<priority_id> \
  category=<category_id> \
  status=1
```

### Priority IDs

| Priority | ID  |
| -------- | --- |
| Critical | 4   |
| High     | 3   |
| Medium   | 2   |
| Low      | 1   |

### Category IDs

| Category      | ID  |
| ------------- | --- |
| Hardware      | 1   |
| Software      | 2   |
| Network       | 3   |
| Configuration | 4   |
| Documentation | 5   |

### Example

```bash
roundup-admin -i tracker create change \
  title="Install monitoring agent on web servers" \
  description="Deploy Prometheus node_exporter on all web servers for system metrics collection" \
  justification="Need visibility into system resource usage and performance metrics" \
  priority=2 \
  category=2 \
  status=1
```

### Get the Change ID

The command outputs the new change ID:

```
5
```

Store it for later use:

```bash
CHANGE_ID=$(roundup-admin -i tracker create change \
  title="..." \
  description="..." \
  justification="..." \
  priority=2 \
  category=2 \
  status=1)

echo "Created change${CHANGE_ID}"
```

## Method 3: API (Recommended for Integration)

### Basic Request

```bash
curl -X POST http://localhost:8080/pms/api/change \
  -H "Content-Type: application/json" \
  -u admin:admin \
  -d '{
    "title": "<title>",
    "description": "<description>",
    "justification": "<justification>",
    "priority": "<priority_id>",
    "category": "<category_id>",
    "status": "1"
  }'
```

### Example

```bash
curl -X POST http://localhost:8080/pms/api/change \
  -H "Content-Type: application/json" \
  -u admin:admin \
  -d '{
    "title": "Rotate SSL certificates",
    "description": "Update SSL certificates on load balancer and web servers before expiration",
    "justification": "Current certificates expire in 7 days, service will fail without renewal",
    "priority": "4",
    "category": "3",
    "status": "1"
  }'
```

### Response

```json
{
  "id": "6",
  "title": "Rotate SSL certificates",
  "status": "planning",
  "created": "2025-11-16.14:30:00"
}
```

### Extract the ID

```bash
CHANGE_ID=$(curl -s -X POST http://localhost:8080/pms/api/change \
  -H "Content-Type: application/json" \
  -u admin:admin \
  -d '{"title":"...","description":"...","justification":"...","priority":"2","category":"2","status":"1"}' \
  | jq -r '.id')

echo "Created change ${CHANGE_ID}"
```

## Adding Optional Fields

### Link to Related Issues

**Web UI**: Use the "Related Issues" section

**CLI**:

```bash
roundup-admin -i tracker set change${CHANGE_ID} issues=5,7,12
```

**API**:

```bash
curl -X PATCH http://localhost:8080/pms/api/change${CHANGE_ID} \
  -H "Content-Type: application/json" \
  -u admin:admin \
  -d '{
    "linked_issues": [5, 7, 12]
  }'
```

### Add Risk and Impact Assessment

**Web UI**: Fill in the "Impact Assessment" and "Risk Assessment" textareas

**CLI**:

```bash
roundup-admin -i tracker set change${CHANGE_ID} \
  impact="Service downtime 30 minutes, affects all users" \
  risk="Low risk - tested in dev environment, rollback plan available"
```

**API**:

```bash
curl -X PATCH http://localhost:8080/pms/api/change${CHANGE_ID} \
  -H "Content-Type: application/json" \
  -u admin:admin \
  -d '{
    "impact": "Service downtime 30 minutes, affects all users",
    "risk": "Low risk - tested in dev environment, rollback plan available"
  }'
```

## Best Practices

### Title

✅ **Good**: "Upgrade PostgreSQL from v14 to v16"
✅ **Good**: "Add firewall rule for monitoring server"
❌ **Bad**: "Database stuff"
❌ **Bad**: "Fix the thing"

### Description

✅ **Good**: Include step-by-step plan

```
1. Create full backup of database
2. Stop application services
3. Run pg_upgrade with --check
4. Perform actual upgrade
5. Update application configuration
6. Restart services
7. Verify connectivity and run smoke tests
```

❌ **Bad**: "Upgrade the database"

### Justification

✅ **Good**: Explain business/technical need

```
Current version (v14) reaches EOL in 6 months. Version 16 provides:
- 20% query performance improvement (tested in dev)
- Better security with row-level security improvements
- Required for upcoming application features
```

❌ **Bad**: "Because we should"

## Common Scenarios

### Emergency Change (Security Patch)

```bash
roundup-admin -i tracker create change \
  title="Apply critical security patch CVE-2024-12345" \
  description="Install security update for OpenSSL to fix remote code execution vulnerability" \
  justification="Critical security vulnerability actively being exploited in the wild" \
  priority=4 \
  category=2 \
  status=1
```

### Routine Maintenance

```bash
roundup-admin -i tracker create change \
  title="Monthly database backup verification" \
  description="Test restore of last month's database backups to ensure recoverability" \
  justification="Regular verification ensures backups are usable in disaster recovery scenario" \
  priority=2 \
  category=4 \
  status=1
```

### Hardware Addition

```bash
roundup-admin -i tracker create change \
  title="Install additional 32GB RAM in database server" \
  description="Add 2x16GB DDR4 modules to db-prod-01, bringing total to 64GB" \
  justification="Database memory usage consistently above 80%, causing performance degradation" \
  priority=3 \
  category=1 \
  status=1
```

## Troubleshooting

**Q: I get "Permission denied" error**
A: Ensure you're logged in with appropriate permissions. Change creation typically requires "Developer" or "Manager" role.

**Q: The CLI command fails with "Unknown property"**
A: Check field names match the schema exactly. Use `roundup-admin -i tracker spec change` to see all fields.

**Q: My change isn't showing in the list**
A: Check your filter settings. New changes default to "Planning" status.

**Q: Can I create a change on behalf of someone else?**
A: Yes, use the `creator` field (requires admin permissions):

```bash
roundup-admin -i tracker create change \
  title="..." \
  description="..." \
  justification="..." \
  creator=5 \
  priority=2 \
  category=2 \
  status=1
```

## Next Steps

After creating your change request:

1. **Add risk assessment** - See "How-to: Assessing Change Risk"
1. **Get approval** - Move through the workflow states
1. **Schedule implementation** - Set maintenance window
1. **Track execution** - Document actual implementation

## Related Documentation

- **Tutorial**: Managing Changes in Your Homelab - Full walkthrough
- **Reference**: Change Workflow States - All possible states and transitions
- **Explanation**: ITIL Change Management Principles - Understanding the methodology
