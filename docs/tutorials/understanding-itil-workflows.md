<!--
SPDX-FileCopyrightText: 2025 Georges Martin <jrjsmrtn@gmail.com>
SPDX-License-Identifier: MIT
-->

# Understanding ITIL Workflows in PMS

This tutorial introduces you to ITIL-inspired workflows in the Pasture Management System (PMS) and shows you how to use them to manage your homelab infrastructure more effectively.

## What is ITIL?

**ITIL** (Information Technology Infrastructure Library) is a set of best practices for IT service management. While ITIL is designed for large organizations, its core concepts are valuable for homelab administrators who want to:

- Track problems systematically
- Manage changes safely
- Maintain a configuration database
- Follow consistent processes

PMS adapts ITIL concepts to be lightweight and practical for small-scale environments.

## Learning Objectives

By the end of this tutorial, you will:

1. Understand the issue lifecycle workflow
2. Know how to transition issues through different states
3. Recognize valid and invalid status transitions
4. Use workflows to track work progress
5. Apply ITIL concepts to homelab management

## The Issue Lifecycle

In PMS, every issue follows a defined lifecycle from creation to closure. This lifecycle helps you track progress and ensures nothing gets lost.

### Issue Statuses

PMS uses four core statuses inspired by ITIL Incident Management:

| Status | Description | What it means |
|--------|-------------|---------------|
| **New** | Just reported | Issue has been created but not yet reviewed |
| **In Progress** | Being worked on | Someone is actively investigating or fixing the issue |
| **Resolved** | Fix implemented | The fix is complete and ready for verification |
| **Closed** | Verified and done | The fix has been confirmed and the issue is complete |

### Why Multiple Statuses?

You might wonder: "Why not just 'Open' and 'Closed'?"

Multiple statuses provide:

- **Visibility**: See what's being worked on vs. what's waiting
- **Accountability**: Know who's responsible at each stage
- **Workflow**: Enforce quality checks (e.g., verify fixes before closing)
- **Metrics**: Measure how long issues spend in each stage

## Valid Status Transitions

Not all status changes are allowed. PMS enforces valid transitions to maintain data quality.

### The Workflow Diagram

```
    New
     |
     v
In Progress
     |
     v
  Resolved
     |
     v
  Closed
```

### Valid Transitions

| From | To | When to use |
|------|-----|-------------|
| New | In Progress | You start investigating or fixing the issue |
| In Progress | Resolved | You've implemented a fix |
| Resolved | Closed | You've verified the fix works |
| Resolved | In Progress | The fix didn't work; you need to rework it |

### Invalid Transitions

These transitions are **blocked** by PMS:

- ❌ New → Resolved (you can't mark something resolved without working on it)
- ❌ New → Closed (you can't close something without fixing it)
- ❌ In Progress → Closed (you must mark it resolved first for verification)

## Hands-On: Managing Issue Lifecycle

Let's walk through a real example: fixing a failed backup job.

### Step 1: Create the Issue

```bash
# Using CLI
roundup-admin -i tracker create issue \
  title="Backup job failed on NAS" \
  priority=2 \
  status=1

# Issue is created with status "New"
```

Or via Web UI:
1. Navigate to http://localhost:8080/pms
2. Click "Create New Issue"
3. Fill in title: "Backup job failed on NAS"
4. Select priority: "Urgent"
5. Click "Submit" (status defaults to "New")

### Step 2: Start Working on It

When you begin investigating:

**Web UI**:
1. Open the issue
2. Click "Start Work"
3. Status changes to "In Progress"

**CLI**:
```bash
roundup-admin -i tracker set issue1 status=2
```

**API**:
```bash
curl -X PATCH http://localhost:8080/pms/api/issues/1 \
  -H "Content-Type: application/json" \
  -u admin:admin \
  -d '{"status": "2"}'
```

### Step 3: Mark as Resolved

After fixing the backup job configuration:

**Web UI**:
1. Open the issue
2. Add a message: "Fixed cron schedule and verified backup runs"
3. Click "Mark Resolved"

**CLI**:
```bash
roundup-admin -i tracker set issue1 status=3
```

### Step 4: Verify and Close

After confirming the backup runs successfully:

**Web UI**:
1. Open the issue
2. Add a message: "Verified backup completed successfully on 2025-11-16"
3. Click "Close Issue"

**CLI**:
```bash
roundup-admin -i tracker set issue1 status=4
```

## Understanding Status History

PMS automatically tracks every status change with:

- **Timestamp**: When the change occurred
- **User**: Who made the change
- **Previous status**: What it was before
- **New status**: What it changed to

### Viewing History

**Web UI**: Scroll to "History" section on issue details page

**CLI**:
```bash
roundup-admin -i tracker history issue1
```

This audit trail helps you:
- See how long issues spent in each state
- Identify bottlenecks (e.g., many issues stuck "In Progress")
- Review who worked on what
- Demonstrate compliance (for professional homelabs)

## Common Workflow Patterns

### Pattern 1: Quick Fix

For simple issues you can fix immediately:

```
New → In Progress → Resolved → Closed
(all transitions in same session)
```

**Example**: Restart a stuck service

### Pattern 2: Investigation Required

For complex issues needing research:

```
New → In Progress (investigation) →
In Progress (testing fix) → Resolved →
Closed
```

**Example**: Debug why a container won't start

### Pattern 3: Fix Didn't Work

When your first fix fails:

```
New → In Progress → Resolved →
(verification fails) →
In Progress → Resolved → Closed
```

**Example**: Applied patch, but issue persists

## ITIL Concepts in Practice

### Incident vs. Problem

- **Incident** (Issue in PMS): Something is broken and needs immediate fixing
- **Problem**: The root cause behind multiple incidents

In PMS, you can link related issues to identify patterns.

### Change Management

Changes are different from issues:

- **Issues** are reactive (fix something broken)
- **Changes** are proactive (plan an upgrade)

PMS separates these for clarity. See the [Change Management Tutorial](change-management.md) for details.

## Best Practices

### 1. Always Use "In Progress" Before "Resolved"

Even for quick fixes, transition through "In Progress" to maintain accurate history.

**Bad**:
```bash
# Don't do this
roundup-admin -i tracker set issue1 status=3  # New → Resolved (blocked!)
```

**Good**:
```bash
roundup-admin -i tracker set issue1 status=2  # New → In Progress
roundup-admin -i tracker set issue1 status=3  # In Progress → Resolved
```

### 2. Add Comments at Each Transition

Document what you did:

```bash
roundup-admin -i tracker set issue1 status=2 \
  messages="+msg1"

roundup-admin -i tracker create msg \
  content="Started investigating. Checked logs and found permission error." \
  author=1
```

### 3. Verify Before Closing

Don't close issues immediately after fixing. Wait to confirm:

- The fix works in production
- No side effects occurred
- The issue doesn't reoccur

### 4. Use Assignee for Accountability

Assign issues to track who's responsible:

```bash
roundup-admin -i tracker set issue1 assignedto=1 status=2
```

## Common Mistakes to Avoid

### ❌ Closing Too Quickly

**Problem**: Marking issues closed before verifying the fix

**Solution**: Always use "Resolved" first, then close after verification

### ❌ Leaving Issues "In Progress" Forever

**Problem**: Starting work but never updating status

**Solution**: Review "In Progress" issues weekly and update them

### ❌ Skipping Status Transitions

**Problem**: Trying to jump from "New" to "Closed"

**Solution**: Follow the workflow path: New → In Progress → Resolved → Closed

## Try It Yourself

### Exercise 1: Complete Issue Lifecycle

1. Create an issue: "Test web server SSL certificate expiration"
2. Transition it to "In Progress"
3. Mark it "Resolved" with a comment
4. Close it with verification note

### Exercise 2: Handle a Failed Fix

1. Create an issue: "NFS mount not working"
2. Mark "In Progress"
3. Mark "Resolved" with fix attempt
4. Transition back to "In Progress" (fix didn't work)
5. Mark "Resolved" with corrected fix
6. Close it

### Exercise 3: View Status History

1. Use any issue from exercises above
2. View its history via Web UI or CLI
3. Observe all status transitions with timestamps

## Next Steps

Now that you understand issue workflows, explore:

- [Change Management Workflows](change-management.md) - Plan infrastructure changes
- [Reference: Status Transitions](../reference/status-transitions.md) - Complete transition matrix
- [How-to: Track Recurring Issues](../howto/track-recurring-issues.md) - Pattern analysis

## Key Takeaways

✅ Issues follow a defined lifecycle: New → In Progress → Resolved → Closed

✅ Status transitions are enforced to maintain data quality

✅ Every status change is tracked with timestamp and user

✅ ITIL workflows help you manage homelab infrastructure systematically

✅ Always verify fixes before closing issues

## Additional Resources

- [ITIL Foundation Concepts](https://www.axelos.com/certifications/itil-service-management/itil-4-foundation)
- [Roundup Documentation](https://roundup-tracker.org/)
- PMS [Architecture Documentation](../architecture/workspace.dsl)

---

**Feedback**: Found an issue with this tutorial? [Open an issue](https://github.com/jrjsmrtn/pasture-management-system/issues) or submit a pull request.
