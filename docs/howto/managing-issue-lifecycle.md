<!--
SPDX-FileCopyrightText: 2025 Georges Martin <jrjsmrtn@gmail.com>
SPDX-License-Identifier: MIT
-->

# How to Manage Issue Lifecycle

## Overview

This guide shows you how to manage issues through their complete lifecycle in the Pasture Management System, from creation through resolution and closure.

**Time Required**: 5-10 minutes per issue
**Difficulty**: Beginner
**Prerequisites**: PMS installed, admin access

## Issue Lifecycle States

Issues in PMS progress through these states:

```
New → Open → In Progress → Resolved → Closed
                ↓
              Feedback (if needed)
```

Each state represents a stage in problem resolution.

## Creating a New Issue

### Via Web UI

1. Navigate to http://localhost:9080/pms/issue?@template=item
1. Fill in required fields:
   - **Title**: Clear, descriptive summary (e.g., "Web server returning 502 errors")
   - **Priority**: Select based on urgency
     - **Critical** (1): System down, data loss
     - **Urgent** (2): Major functionality broken
     - **Bug** (3): Non-critical issue
     - **Feature** (4): Enhancement request
     - **Wish** (5): Nice-to-have
1. Optional fields:
   - **Assignee**: Who will work on this?
   - **Affected CIs**: Link to configuration items (select from dropdown)
   - **Description**: Detailed information, steps to reproduce
1. Click "Submit New Entry"

**Result**: Issue created with status "New" (ready for triage)

### Via CLI

```bash
cd tracker
uv run roundup-admin -i . create issue \
  title="Database connection pool exhausted" \
  priority=2 \
  status=1
```

**Result**: Returns new issue ID (e.g., `issue1`)

### Via REST API

```bash
curl -X POST http://localhost:9080/pms/rest/data/issue \
  -u admin:admin \
  -H "Content-Type: application/json" \
  -H "X-Requested-With: XMLHttpRequest" \
  -H "Origin: http://localhost:9080" \
  -H "Referer: http://localhost:9080/pms/" \
  -d '{
    "title": "NAS running out of disk space",
    "priority": "2",
    "status": "1"
  }'
```

## Triaging New Issues

**Goal**: Review new issues and prioritize for action.

### Review Queue

1. Navigate to http://localhost:9080/pms/issue?status=1 (New issues)
1. Review each issue:
   - Is the title clear?
   - Is the priority correct?
   - Is there enough information to investigate?

### Update Priority

If priority needs adjustment:

```bash
cd tracker
uv run roundup-admin -i . set issue1 priority=3  # Change to Bug
```

### Assign Owner

```bash
cd tracker
uv run roundup-admin -i . set issue1 assignedto=1  # Assign to admin
```

### Link to Affected CIs

If not already linked:

```bash
cd tracker
# Find the CI ID
uv run roundup-admin -i . find ci name=web-server-vm

# Link issue to CI (assuming CI ID is 8)
uv run roundup-admin -i . set issue1 affected_cis=8
```

### Move to Open

Once triaged, mark as Open:

```bash
cd tracker
uv run roundup-admin -i . set issue1 status=2  # Open
```

**Or via Web UI**: Edit issue → Status: "Open" → Submit

## Working on Issues

### Set to In Progress

When you start working:

```bash
cd tracker
uv run roundup-admin -i . set issue1 status=3  # In Progress
```

### Add Updates

**Via Web UI**:

1. Navigate to http://localhost:9080/pms/issue1
1. Scroll to "Add a message"
1. Enter your update:
   ```
   Investigating web server logs. Found repeated errors:
   "upstream timed out (110: Connection timed out)"

   Indicates issue with backend connection to database.
   Next: Check database server connectivity.
   ```
1. Click "Submit Changes"

**Via CLI**:

```bash
cd tracker
uv run roundup-admin -i . create msg \
  content="Confirmed database server is responding. \
           Issue appears to be connection pool configuration. \
           Increasing max_connections from 100 to 200." \
  author=1

# Link message to issue
uv run roundup-admin -i . set issue1 messages=1
```

### Attach Files

**Via Web UI**:

1. Edit issue
1. Click "Choose File" under Attachments
1. Select file (e.g., log excerpt, screenshot)
1. Click "Submit Changes"

**Use Case**: Attach error logs, configuration files, or screenshots showing the problem.

## Resolving Issues

### Mark as Resolved

When the fix is complete:

```bash
cd tracker
uv run roundup-admin -i . set issue1 status=4  # Resolved
```

### Document Resolution

Add a message explaining the fix:

```bash
cd tracker
uv run roundup-admin -i . create msg \
  content="Resolution: Increased database connection pool \
           from 100 to 200 connections in postgresql.conf. \
           Restarted PostgreSQL service. \
           \
           Verified web server no longer showing timeout errors. \
           Monitoring for 24 hours before closing." \
  author=1

uv run roundup-admin -i . set issue1 messages=2
```

**Best Practices**:

- Explain what you did
- Describe how you verified the fix
- Note any monitoring or follow-up needed

### Link to Related Changes

If you created a change request for the fix:

```bash
cd tracker
# Assuming change ID is 5
uv run roundup-admin -i . set issue1 related_changes=5
```

## Requesting Feedback

If you need user confirmation before closing:

```bash
cd tracker
uv run roundup-admin -i . set issue1 status=5  # Feedback
```

Add a message:

```
Fix deployed. Please verify the issue is resolved and report back.
If no issues reported within 24 hours, will close as resolved.
```

## Closing Issues

### Mark as Closed

After verification period:

```bash
cd tracker
uv run roundup-admin -i . set issue1 status=6  # Closed
```

### Document Closure

```bash
cd tracker
uv run roundup-admin -i . create msg \
  content="No further issues reported. \
           Fix verified successful. \
           Closing issue." \
  author=1

uv run roundup-admin -i . set issue1 messages=3
```

## Common Workflows

### Incident Response Workflow

**Scenario**: Production service down

1. **Create Issue** (Priority: Critical)

   ```bash
   cd tracker
   uv run roundup-admin -i . create issue \
     title="Web application down - 502 errors" \
     priority=1 \
     status=3
   ```

1. **Link to Affected CIs**

   ```bash
   cd tracker
   uv run roundup-admin -i . find ci name=web-app-service
   uv run roundup-admin -i . set issue1 affected_cis=11
   ```

1. **Query CI Dependencies** (for impact analysis)

   ```bash
   cd tracker
   uv run roundup-admin -i . find cirelationship source_ci=11
   ```

1. **Add Investigation Notes**

   - Document symptoms
   - List troubleshooting steps
   - Record findings

1. **Resolve and Document**

   - Explain root cause
   - Describe fix
   - Note preventive actions

1. **Close After Monitoring**

   - Verify stability (24-48 hours)
   - Close with final summary

### Bug Tracking Workflow

**Scenario**: Non-critical software bug

1. **Create Issue** (Priority: Bug)
1. **Set Status**: New
1. **Triage**:
   - Reproduce the bug
   - Assess impact
   - Assign to developer
1. **In Progress**:
   - Develop fix
   - Test in development
   - Deploy to production
1. **Resolved**:
   - Document fix
   - Update affected CIs if config changed
1. **Closed**:
   - Verify in production
   - Close with notes

### Feature Request Workflow

**Scenario**: Enhancement request

1. **Create Issue** (Priority: Feature)
1. **Triage**:
   - Assess value vs. effort
   - Get stakeholder input
   - Prioritize in backlog
1. **In Progress**:
   - Design solution
   - Implement
   - Test
1. **Resolved**:
   - Deploy to production
   - Document new functionality
1. **Feedback**:
   - Get user validation
   - Collect feedback
1. **Closed**:
   - Confirm acceptance
   - Close with summary

## Bulk Operations

### Close Multiple Resolved Issues

```bash
cd tracker
# Find all resolved issues older than 7 days
uv run roundup-admin -i . find issue status=4

# Review the list, then close them
for issue_id in $(uv run roundup-admin -i . find issue status=4); do
  uv run roundup-admin -i . set issue$issue_id status=6
done
```

### Reassign Multiple Issues

```bash
cd tracker
# Find all issues assigned to user 2
uv run roundup-admin -i . find issue assignedto=2

# Reassign to user 3
for issue_id in $(uv run roundup-admin -i . find issue assignedto=2); do
  uv run roundup-admin -i . set issue$issue_id assignedto=3
done
```

## Reporting

### Active Issues by Priority

```bash
cd tracker
# Find all open/in-progress critical issues
uv run roundup-admin -i . find issue priority=1 status=2,3

# Find all open/in-progress urgent issues
uv run roundup-admin -i . find issue priority=2 status=2,3
```

### Issues by Affected CI

```bash
cd tracker
# Find all issues affecting a specific CI (e.g., ci8)
uv run roundup-admin -i . find issue affected_cis=8
```

**Use Case**: Before doing maintenance on a CI, check if there are open issues.

### Issues Opened This Month

**Via Web UI**:

Navigate to http://localhost:9080/pms/issue?@sort=creation&@filter=creation

Adjust date range filter to current month.

## Best Practices

### Clear Titles

❌ Bad: "Server problem"
✅ Good: "Web server returning 502 errors on /api endpoint"

❌ Bad: "Network slow"
✅ Good: "LAN transfer speeds degraded from 1Gbps to 100Mbps"

### Detailed Descriptions

Include:

- **Symptoms**: What is happening?
- **Impact**: What's affected?
- **When**: When did it start?
- **Steps to Reproduce**: How to see the problem?

Example:

```
Symptoms: Web application returns HTTP 502 Bad Gateway error
Impact: All users unable to access the application
When: Started at 2025-11-20 14:30 UTC
Steps to Reproduce:
  1. Navigate to https://homelab.example.com/app
  2. Observe 502 error page
```

### Regular Updates

Add updates at key milestones:

- When investigation starts
- When root cause identified
- When fix deployed
- When verification complete

### Link Related Items

Always link:

- **Affected CIs**: Infrastructure components involved
- **Related Changes**: Change requests for fixes
- **Related Issues**: Duplicate or related problems

### Use Appropriate Priorities

- **Critical (1)**: Production down, data loss, security breach

  - Response time: Immediate
  - Escalation: Notify all stakeholders

- **Urgent (2)**: Major functionality broken

  - Response time: Within 1 hour
  - Escalation: Notify manager

- **Bug (3)**: Non-critical issues

  - Response time: Within 1 day
  - Escalation: Normal workflow

- **Feature (4)**: Enhancement requests

  - Response time: Next planning cycle
  - Escalation: None

- **Wish (5)**: Nice-to-have

  - Response time: Backlog
  - Escalation: None

## Troubleshooting

### Issue Status Won't Change

**Problem**: Cannot change issue status in Web UI

**Solution**: Check permissions. Admin users can change status. Non-admin users may have restricted permissions.

### Can't Link CI to Issue

**Problem**: CI doesn't appear in dropdown

**Solution**: Reindex CIs:

```bash
cd tracker
uv run roundup-admin -i . reindex ci
```

Restart server:

```bash
pkill -f roundup-server && sleep 2
uv run roundup-server -p 9080 pms=tracker > /dev/null 2>&1 &
```

### Message Didn't Attach to Issue

**Problem**: Created message but it's not linked to issue

**Solution**: Explicitly set the messages field:

```bash
cd tracker
# Get current messages (if any)
uv run roundup-admin -i . get issue1 messages

# Add new message ID to the list
uv run roundup-admin -i . set issue1 messages=1,2,3  # Include new message ID
```

## Next Steps

- **How-to**: [Documenting Infrastructure Dependencies](./documenting-infrastructure-dependencies.md)
- **Tutorial**: [Getting Started](../tutorials/getting-started.md)

## Summary

You now know how to:

✅ Create issues via Web UI, CLI, and API
✅ Triage and prioritize new issues
✅ Assign ownership and link to CIs
✅ Progress issues through lifecycle states
✅ Document investigation and resolution
✅ Close issues with proper verification
✅ Use bulk operations for efficiency
✅ Apply best practices for issue management
