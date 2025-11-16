<!--
SPDX-FileCopyrightText: 2025 Georges Martin <jrjsmrtn@gmail.com>
SPDX-License-Identifier: MIT
-->

# How-to: Assess Change Risk

**Goal**: Properly evaluate and document the risk and impact of a proposed change.

**Time**: 10-15 minutes per change

## Overview

Risk assessment helps you make informed decisions about whether to proceed with a change and how to mitigate potential problems. A good risk assessment includes:

- **Impact analysis** - What happens if this change is implemented?
- **Risk identification** - What could go wrong?
- **Mitigation strategies** - How do we reduce risk?
- **Rollback plan** - How do we undo this if needed?

## Impact Assessment Framework

### Questions to Ask

1. **Who is affected?**

   - All users, specific teams, administrators only?
   - Internal systems, external services, both?

1. **How long will it take?**

   - Total downtime duration
   - Degraded performance period
   - Time to full recovery

1. **What services are impacted?**

   - Critical services (authentication, database, network)
   - Important services (monitoring, backup, logging)
   - Nice-to-have services (dashboards, reporting)

1. **When can this be done?**

   - Must be during business hours?
   - Can wait for maintenance window?
   - Emergency - must be done immediately?

### Impact Levels

| Level       | Description                             | Example                                    |
| ----------- | --------------------------------------- | ------------------------------------------ |
| **None**    | No service impact                       | Documentation update, configuration backup |
| **Minimal** | < 5 min downtime, non-critical service  | Update monitoring dashboard                |
| **Low**     | 5-30 min downtime, degraded performance | Restart non-critical service               |
| **Medium**  | 30-120 min downtime, partial outage     | Database minor version upgrade             |
| **High**    | > 2 hours downtime, major outage        | Infrastructure migration                   |

### Writing the Impact Assessment

**Template**:

```
Service Impact: [None/Minimal/Low/Medium/High]

Affected Services:
- [Service 1]: [Impact description]
- [Service 2]: [Impact description]

Affected Users:
- [User group]: [How they're affected]

Timing:
- Estimated duration: [X minutes/hours]
- Scheduled window: [Date/time]
- Best time to execute: [When and why]

Dependencies:
- [System/service that must be available]
- [Team/person that must be present]
```

**Example**:

```
Service Impact: Medium

Affected Services:
- Database: Full outage during upgrade (est. 90 minutes)
- Web applications: Unavailable (depends on database)
- API services: Unavailable (depends on database)
- Monitoring: Remains operational
- Backup services: Remains operational

Affected Users:
- All end users: No access to applications
- Administrators: Can monitor progress
- Automated jobs: Will queue and retry

Timing:
- Estimated duration: 90 minutes (upgrade) + 30 minutes (verification)
- Scheduled window: Saturday 02:00-05:00 AM
- Best time to execute: Early Saturday morning (minimal user impact)

Dependencies:
- Full backup completed and verified
- Database administrator available
- Rollback procedure tested in development
```

## Risk Assessment Framework

### Risk Identification

Consider these categories:

1. **Technical Risks**

   - Software compatibility issues
   - Hardware failures during change
   - Data corruption or loss
   - Network connectivity problems
   - Performance degradation

1. **Operational Risks**

   - Insufficient testing
   - Inadequate documentation
   - Key personnel unavailable
   - Time constraints
   - Complex rollback procedure

1. **Business Risks**

   - Extended downtime
   - Lost revenue
   - Compliance violations
   - Security vulnerabilities introduced
   - Reputation damage

### Risk Levels

Use this matrix to assess risk level:

| Impact / Likelihood  | Very Low | Low      | Medium | High      | Very High |
| -------------------- | -------- | -------- | ------ | --------- | --------- |
| **Very High Impact** | Medium   | High     | High   | Very High | Very High |
| **High Impact**      | Low      | Medium   | High   | High      | Very High |
| **Medium Impact**    | Low      | Low      | Medium | High      | High      |
| **Low Impact**       | Very Low | Low      | Low    | Medium    | High      |
| **Very Low Impact**  | Very Low | Very Low | Low    | Medium    | Medium    |

**Likelihood Criteria**:

- **Very Low**: < 5% chance
- **Low**: 5-20% chance
- **Medium**: 20-50% chance
- **High**: 50-80% chance
- **Very High**: > 80% chance

### Writing the Risk Assessment

**Template**:

```
Overall Risk Level: [Very Low/Low/Medium/High/Very High]

Identified Risks:
1. [Risk description]
   - Likelihood: [Level]
   - Impact if occurs: [Level]
   - Mitigation: [How to prevent/reduce]

2. [Next risk...]

Rollback Plan:
- Trigger criteria: [When to rollback]
- Rollback procedure: [Steps to undo]
- Rollback duration: [Time estimate]
- Testing status: [Tested in dev? Verified backup?]

Success Criteria:
- [How do we know it worked?]
- [What tests must pass?]
```

**Example - Low Risk**:

```
Overall Risk Level: Low

Identified Risks:
1. Configuration file syntax error
   - Likelihood: Low (changes reviewed by 2 people)
   - Impact if occurs: Low (service fails to start, easily corrected)
   - Mitigation: Pre-validate configuration with --check flag

2. Service restart takes longer than expected
   - Likelihood: Medium (large dataset to reload)
   - Impact if occurs: Very Low (just extends downtime slightly)
   - Mitigation: Extended maintenance window by 30 minutes

Rollback Plan:
- Trigger criteria: Service fails to start after 2 retry attempts
- Rollback procedure: Restore previous config file, restart service
- Rollback duration: < 5 minutes
- Testing status: Rollback tested in development environment

Success Criteria:
- Service starts successfully
- Health check endpoint returns 200 OK
- Monitoring shows normal metrics within 5 minutes
```

**Example - High Risk**:

```
Overall Risk Level: High

Identified Risks:
1. Database migration fails on production dataset size
   - Likelihood: Medium (tested on dev, but prod is 10x larger)
   - Impact if occurs: High (extended downtime, possible data loss)
   - Mitigation: Additional testing with production-sized dataset,
                 pre-allocate disk space, increase timeout limits

2. Application incompatible with new database version
   - Likelihood: Low (tested in staging)
   - Impact if occurs: Very High (complete service outage)
   - Mitigation: Parallel testing in staging for 1 week,
                 all integration tests must pass

3. Rollback takes too long, exceeds maintenance window
   - Likelihood: Medium (large backup to restore)
   - Impact if occurs: High (extended outage)
   - Mitigation: Use faster restore method (parallel restore),
                 extend maintenance window to 4 hours

Rollback Plan:
- Trigger criteria:
  * Migration runs > 3 hours
  * Critical errors in migration log
  * Post-migration validation tests fail
- Rollback procedure:
  1. Stop all application services
  2. Restore database from backup (tested restore: 45 minutes)
  3. Verify data integrity
  4. Restart services
  5. Run smoke tests
- Rollback duration: 60-90 minutes
- Testing status:
  * Full backup completed 30 minutes before change
  * Restore tested successfully (45 minute restore time)
  * Verification procedures documented and tested

Success Criteria:
- Database upgrade completes successfully
- All migration scripts execute without errors
- Application connects and authenticates
- Sample queries return expected results
- Performance metrics within 10% of baseline
- All scheduled jobs execute successfully
```

## Step-by-Step Process

### 1. Gather Information

Before assessing, collect:

- Change description and technical details
- System documentation
- Similar past changes and their outcomes
- Test results from development/staging
- Backup status and restore time estimates

### 2. Assess Impact

Use the Web UI, CLI, or API:

**Web UI**:

1. Open the change
1. Fill in "Impact Assessment" field with structured analysis
1. Click Submit

**CLI**:

```bash
roundup-admin -i tracker set change1 impact="$(cat <<EOF
Service Impact: Medium

Affected Services:
- Database: Full outage (90 min)
- Web apps: Unavailable
- API: Unavailable

Affected Users: All users

Timing:
- Duration: 90-120 minutes
- Window: Saturday 02:00-05:00
- Best time: Early AM (low usage)

Dependencies:
- Full backup verified
- DBA available
- Rollback tested
EOF
)"
```

**API**:

```bash
curl -X PATCH http://localhost:8080/pms/api/change1 \
  -H "Content-Type: application/json" \
  -u admin:admin \
  -d '{
    "impact": "Service Impact: Medium\n\nAffected Services:\n- Database: Full outage (90 min)\n..."
  }'
```

### 3. Assess Risk

**Web UI**:

1. Fill in "Risk Assessment" field
1. Click Submit

**CLI**:

```bash
roundup-admin -i tracker set change1 risk="$(cat <<EOF
Overall Risk Level: Medium

Identified Risks:
1. Migration failure on large dataset
   - Likelihood: Low
   - Impact: High
   - Mitigation: Pre-tested, extended window

Rollback Plan:
- Trigger: Migration > 3 hours or errors
- Procedure: Restore from backup (45 min)
- Status: Tested successfully

Success Criteria:
- Upgrade completes successfully
- All tests pass
- Performance within 10% baseline
EOF
)"
```

### 4. Review and Adjust

- Review with a colleague if possible
- Consider edge cases
- Verify rollback plan is realistic
- Ensure success criteria are measurable

### 5. Update Based on Testing

After testing in development:

```bash
roundup-admin -i tracker set change1 risk="$(cat <<EOF
[Previous risk assessment]

Update after Development Testing:
- Test migration completed in 45 minutes
- All application tests passed
- Performance improved by 15%
- Rollback tested successfully (40 minute restore)

Risk level reduced from High to Medium based on successful testing.
EOF
)"
```

## Common Pitfalls

❌ **Being overly optimistic**
"This is a simple change, nothing will go wrong"
✅ **Better**: Identify specific risks even for "simple" changes

❌ **Vague impact descriptions**
"Some downtime may occur"
✅ **Better**: "Estimated 30-45 minute service outage affecting all users"

❌ **No rollback plan**
"We'll figure it out if something goes wrong"
✅ **Better**: Document and test rollback procedure in advance

❌ **Untested assumptions**
"The backup should work"
✅ **Better**: "Backup verified with test restore completed in 20 minutes"

❌ **Ignoring dependencies**
"Just upgrade the database"
✅ **Better**: "Requires: backup completion, DBA availability, application compatibility verified"

## Risk Mitigation Strategies

### General Strategies

1. **Test First**: Always test in development/staging
1. **Backup Everything**: Full, verified backups before major changes
1. **Plan Rollback**: Document and test rollback procedure
1. **Extend Windows**: Add buffer time to estimates
1. **Monitor Closely**: Watch metrics during and after change
1. **Document Everything**: Record what actually happened

### Specific Mitigations

| Risk                   | Mitigation                                         |
| ---------------------- | -------------------------------------------------- |
| Data loss              | Full backup, verified restore, transaction logging |
| Extended downtime      | Parallel systems, faster rollback, extended window |
| Performance issues     | Load testing, monitoring alerts, rollback criteria |
| Compatibility problems | Integration testing, phased rollout, feature flags |
| Human error            | Peer review, checklists, automation where possible |

## Approval Guidelines

Based on risk level, different approval may be needed:

| Risk Level | Approval Required      | Notes                                       |
| ---------- | ---------------------- | ------------------------------------------- |
| Very Low   | Self-approve           | Document in change request                  |
| Low        | Peer review            | Another admin reviews                       |
| Medium     | Manager approval       | Formal approval process                     |
| High       | Manager + stakeholder  | Business impact review                      |
| Very High  | Emergency change board | Detailed review, may require testing period |

## Next Steps

After completing risk assessment:

1. **Submit for approval** - Move change to "Assessment" status
1. **Address feedback** - Update assessment based on reviewer comments
1. **Schedule change** - Once approved, set maintenance window
1. **Monitor execution** - Track actual vs. assessed risk

## Related Documentation

- **Tutorial**: Managing Changes in Your Homelab - Full change lifecycle
- **How-to**: Submit a Change Request - Creating the initial change
- **Reference**: Change Workflow States - Understanding approval process
- **Explanation**: ITIL Change Management Principles - Why we assess risk
