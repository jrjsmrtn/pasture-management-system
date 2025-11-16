<!--
SPDX-FileCopyrightText: 2025 Georges Martin <jrjsmrtn@gmail.com>
SPDX-License-Identifier: MIT
-->

# Tutorial: Managing Changes in Your Homelab

**Learning Goal**: By the end of this tutorial, you'll understand how to use the Pasture Management System to plan, assess, schedule, and track changes in your homelab environment using ITIL-inspired change management practices.

**Estimated Time**: 30 minutes

## What You'll Learn

- How to create and submit a change request
- How to assess risk and impact for changes
- How to schedule changes for maintenance windows
- How to track implementation and document outcomes
- How to link changes to related issues

## Prerequisites

- Pasture Management System installed and running
- Access to the web UI (or familiarity with CLI/API)
- At least one issue in your tracker (we'll link a change to it)

## Scenario

You've noticed that your homelab database server is running PostgreSQL 14, but version 16 offers better performance and security. You want to upgrade during your next maintenance window while properly documenting the change for future reference.

## Step 1: Create a Change Request

A change request captures *what* you want to do and *why* it's necessary.

### Via Web UI

1. Navigate to **Changes** in the main menu

1. Click **Create New Change**

1. Fill in the change details:

   - **Title**: "Upgrade PostgreSQL from v14 to v16"
   - **Description**: "Upgrade database server to PostgreSQL 16 for improved performance and security features"
   - **Justification**: "Current version approaching EOL, security patches needed, performance improvements available"
   - **Priority**: High
   - **Category**: Software
   - **Status**: Planning

1. Click **Submit**

**Result**: Your change is created with status "Planning" and assigned a change ID (e.g., change1).

### Via CLI

```bash
roundup-admin -i tracker create change \
  title="Upgrade PostgreSQL from v14 to v16" \
  description="Upgrade database server to PostgreSQL 16" \
  justification="Security and performance improvements" \
  priority=3 \
  category=2 \
  status=1
```

### Via API

```bash
curl -X POST http://localhost:8080/pms/api/change \
  -H "Content-Type: application/json" \
  -u admin:admin \
  -d '{
    "title": "Upgrade PostgreSQL from v14 to v16",
    "description": "Upgrade database server to PostgreSQL 16",
    "justification": "Security and performance improvements",
    "priority": "3",
    "category": "2",
    "status": "1"
  }'
```

## Step 2: Link the Change to a Related Issue

If you have an existing issue about database performance or security, link it to your change.

### Via Web UI

1. Open your change (change1)
1. Scroll to the **Related Issues** section
1. Click **Add Related Issue**
1. Select the issue (e.g., "Database performance slow")
1. Click **Link**

**Result**: The change and issue are now linked. You can see the relationship from both sides.

### Via CLI

```bash
# Assuming issue5 exists
roundup-admin -i tracker set change1 issues=5
```

## Step 3: Assess Risk and Impact

Before approving a change, assess its risk and potential impact.

### Via Web UI

1. Open your change (change1)

1. Fill in the **Impact Assessment**:

   ```
   Service downtime 1-2 hours during upgrade.
   All applications using the database will be unavailable.
   Backup window extended by 30 minutes.
   ```

1. Fill in the **Risk Assessment**:

   ```
   Risk: Medium
   - Database migration may fail on large datasets
   - Application compatibility issues possible
   - Rollback plan: Full backup before upgrade, tested restore procedure
   ```

1. Click **Submit**

**Result**: Risk and impact are documented and visible to anyone reviewing the change.

### Via CLI

```bash
roundup-admin -i tracker set change1 \
  impact="Service downtime 1-2 hours during upgrade" \
  risk="Medium risk - backup and rollback plan in place"
```

## Step 4: Move Through Approval Workflow

Changes must be assessed and approved before implementation.

### Transition to Assessment

1. Open your change
1. Click **Start Assessment**
1. Status changes to "Assessment"

### Add Assessment Notes

In the notes/messages section, document your assessment:

```
Assessment complete:
- Risk: Medium (mitigated with backup/rollback plan)
- Impact: 1-2 hour downtime (acceptable for maintenance window)
- Prerequisites: Full backup verified, test migration successful
- Recommendation: Approve for Saturday 2 AM maintenance window
```

### Approve the Change

1. Click **Approve**
1. Status changes to "Approved"

**Note**: In a team environment, a different person would perform the approval.

## Step 5: Schedule the Change

Now that the change is approved, schedule it for a maintenance window.

### Via Web UI

1. Open your change

1. Fill in scheduling information:

   - **Scheduled Date**: 2025-12-07
   - **Start Time**: 02:00
   - **End Time**: 04:00

1. Click **Submit**

**Result**: Status changes to "Scheduled" and the change appears in your scheduled changes list.

### Via CLI

```bash
roundup-admin -i tracker set change1 \
  scheduled_start="2025-12-07.02:00:00" \
  scheduled_end="2025-12-07.04:00:00" \
  status=scheduled
```

## Step 6: Begin Implementation

When your maintenance window arrives, start tracking the implementation.

### Via Web UI

1. Open your change
1. Click **Start Implementation**
1. Status changes to "Implementing"
1. Actual start time is automatically recorded

**Result**: The change is now actively being implemented.

## Step 7: Document Implementation

As you perform the upgrade, document what actually happens.

### Fill in Implementation Notes

1. While still on the change details page, scroll to **Implementation Notes**

1. Document your progress:

   ```
   02:05 - Stopped all database connections
   02:10 - Created full backup (verified)
   02:15 - Began PostgreSQL upgrade
   02:45 - Upgrade completed, started database
   02:50 - Ran migration scripts
   03:00 - Verified all applications connecting successfully
   03:15 - All tests passed, monitoring for issues
   ```

1. Fill in **Actual Duration**: 70 minutes

### Document Any Deviations

If things didn't go as planned:

```
Deviation: Upgrade took 70 minutes instead of planned 60 minutes.
Reason: Migration scripts took longer than expected on production dataset.
Impact: Still within 2-hour maintenance window, no issues.
```

## Step 8: Complete the Change

Once the upgrade is successful and verified, mark the change complete.

### Via Web UI

1. Select **Implementation Outcome**: Success
1. Click **Mark Complete**
1. Status changes to "Completed"
1. Actual end time is automatically recorded

**Result**: The change is completed and fully documented.

### Via CLI

```bash
roundup-admin -i tracker set change1 \
  status=completed \
  actual_end="2025-12-07.03:15:00" \
  implementation_notes="Upgrade successful, all tests passed"
```

## Alternative: Handling Rollback

If something goes wrong during implementation, you can document a rollback.

### Via Web UI

1. While in "Implementing" status, click **Rollback**

1. Enter **Rollback Reason**:

   ```
   Migration failed validation tests on production dataset.
   Critical stored procedures incompatible with v16.
   ```

1. Enter **Rollback Notes**:

   ```
   Restored from backup taken at 02:10.
   All services verified operational by 03:00.
   Total downtime: 55 minutes.
   ```

1. Click **Confirm Rollback**

1. Status changes to "Cancelled"

**Result**: The rollback is documented for future reference and learning.

## What You've Learned

You now know how to:

✅ Create a change request with proper justification
✅ Link changes to related issues for traceability
✅ Assess risk and impact before approval
✅ Navigate the approval workflow (Planning → Assessment → Approved)
✅ Schedule changes for maintenance windows
✅ Track actual implementation with notes
✅ Document deviations from the plan
✅ Complete changes successfully or handle rollbacks

## Next Steps

- **How-to: Submitting a Change Request** - Quick reference for creating changes
- **How-to: Assessing Change Risk** - Detailed guidance on risk assessment
- **Reference: Change Workflow States** - Complete state transition reference
- **Explanation: ITIL Change Management Principles** - Understanding the methodology

## Real-World Tips

1. **Always create a backup** before major changes, even if you think you don't need one
1. **Test in a dev environment** first whenever possible
1. **Schedule changes during low-usage periods** to minimize impact
1. **Document everything** - your future self will thank you
1. **Link to related issues** - it creates a valuable history
1. **Be honest about deviations** - they're learning opportunities
1. **Use the rollback procedure** without hesitation if things go wrong

## Common Pitfalls

- **Skipping risk assessment** - Always assess risk, even for "simple" changes
- **Not testing rollback** - Verify your rollback procedure works before you need it
- **Poor documentation** - Write implementation notes as you go, not after
- **Underestimating time** - Add buffer time to your estimates
- **Ignoring dependencies** - Check what else relies on what you're changing

## Troubleshooting

**Q: Can I edit a change after it's approved?**
A: You can add notes and update scheduled times, but major changes should go through re-assessment.

**Q: What if I need to reschedule?**
A: Update the scheduled_start and scheduled_end times. The history will show the change.

**Q: How do I see all scheduled changes?**
A: Navigate to Changes and filter by status="Scheduled" or view the change calendar.

**Q: Can I link multiple issues to one change?**
A: Yes! Add as many related issues as needed to track all related problems.

______________________________________________________________________

**Congratulations!** You've completed the "Managing Changes in Your Homelab" tutorial. You're now ready to implement professional change management in your homelab environment.
